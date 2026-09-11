"""
Trains the GDNLite model per SMD machine and produces anomaly scores + status
labels for every timestep of the test set. Results are saved as one Parquet-free
CSV per machine (results/<machine>.csv) plus a summary.json used by the
FastAPI backend and Streamlit dashboard.

Usage: python3 train_and_infer.py
"""
import os
import sys
import json
import time
import numpy as np
import pandas as pd
import torch
import torch.nn as nn

sys.path.append(os.path.dirname(__file__))
from models.gnn_model import GDNLite

DATA_DIR = os.path.join(os.path.dirname(__file__), "data", "omni", "ServerMachineDataset")
RESULTS_DIR = os.path.join(os.path.dirname(__file__), "results")
os.makedirs(RESULTS_DIR, exist_ok=True)

WINDOW = 10
HIDDEN_DIM = 16
EMBED_DIM = 8
EPOCHS = 2
BATCH_SIZE = 512
LR = 3e-3
DEVICE = "cuda" if torch.cuda.is_available() else "cpu"

# SMD's 38 raw dims don't have official public names; we group them into
# 4 human-readable categories (CPU/Load, Memory, Disk, Network) for the
# dashboard, spreading the 38 channels evenly across the 4 groups.
GROUP_NAMES = ["CPU / Load", "Memory", "Disk", "Network"]


def load_machine(machine_id):
    train = np.loadtxt(os.path.join(DATA_DIR, "train", f"{machine_id}.txt"), delimiter=",")
    test = np.loadtxt(os.path.join(DATA_DIR, "test", f"{machine_id}.txt"), delimiter=",")
    labels = np.loadtxt(os.path.join(DATA_DIR, "test_label", f"{machine_id}.txt"), delimiter=",")
    return train.astype(np.float32), test.astype(np.float32), labels.astype(np.int32)


def make_windows(arr, window):
    # arr: (T, N) -> X: (T-window, window, N), y: (T-window, N)
    T = arr.shape[0]
    X, y = [], []
    for t in range(window, T):
        X.append(arr[t - window:t])
        y.append(arr[t])
    return np.stack(X), np.stack(y)


def train_one_machine(machine_id, subsample_every=4, verbose=False):
    train, test, labels = load_machine(machine_id)
    num_nodes = train.shape[1]

    # light subsampling of the (very long) train set to keep training fast
    train_ds = train[::subsample_every]
    Xtr, ytr = make_windows(train_ds, WINDOW)
    Xte, yte = make_windows(test, WINDOW)
    labels_aligned = labels[WINDOW:]  # align labels with prediction targets

    Xtr_t = torch.tensor(Xtr)
    ytr_t = torch.tensor(ytr)
    Xte_t = torch.tensor(Xte)

    model = GDNLite(num_nodes=num_nodes, window_size=WINDOW,
                     embed_dim=EMBED_DIM, hidden_dim=HIDDEN_DIM, topk=10).to(DEVICE)
    opt = torch.optim.Adam(model.parameters(), lr=LR)
    loss_fn = nn.MSELoss()

    n = Xtr_t.shape[0]
    model.train()
    for epoch in range(EPOCHS):
        perm = torch.randperm(n)
        total_loss = 0.0
        for i in range(0, n, BATCH_SIZE):
            idx = perm[i:i + BATCH_SIZE]
            xb = Xtr_t[idx].to(DEVICE)
            yb = ytr_t[idx].to(DEVICE)
            opt.zero_grad()
            pred = model(xb)
            loss = loss_fn(pred, yb)
            loss.backward()
            opt.step()
            total_loss += loss.item() * xb.size(0)
        if verbose:
            print(f"  [{machine_id}] epoch {epoch+1}/{EPOCHS} loss={total_loss/n:.5f}")

    # Inference on test set
    model.eval()
    errors = []
    with torch.no_grad():
        for i in range(0, Xte_t.shape[0], BATCH_SIZE):
            xb = Xte_t[i:i + BATCH_SIZE].to(DEVICE)
            pred = model(xb).cpu().numpy()
            actual = yte[i:i + BATCH_SIZE]
            errors.append(np.abs(pred - actual))
    errors = np.concatenate(errors, axis=0)  # (T_test, num_nodes)

    # Per-sensor robust normalization (median/MAD) -> per-timestep max deviation
    # score, same spirit as GDN's deviation scoring.
    med = np.median(errors, axis=0, keepdims=True)
    mad = np.median(np.abs(errors - med), axis=0, keepdims=True) + 1e-6
    norm_errors = (errors - med) / mad
    raw_score = norm_errors.max(axis=1)
    # squash to a 0-1 "anomaly score" via a smooth cap for dashboard readability
    score = 1 - np.exp(-np.clip(raw_score, 0, None) / 8.0)

    return {
        "machine_id": machine_id,
        "num_nodes": num_nodes,
        "score": score,
        "labels": labels_aligned,
        "per_metric_error": norm_errors,
        "raw_test": test[WINDOW:],
    }


def summarize_groups(raw_test_row, num_nodes):
    """Map raw 38-dim SMD row into 4 pseudo-metric groups (0-100%)."""
    idx_groups = np.array_split(np.arange(num_nodes), 4)
    vals = []
    for grp in idx_groups:
        v = float(np.clip(raw_test_row[grp].mean(), 0, 1) * 100)
        vals.append(round(v, 1))
    return dict(zip(GROUP_NAMES, vals))


def main():
    machines = sorted(
        f.replace(".txt", "") for f in os.listdir(os.path.join(DATA_DIR, "train"))
        if f.endswith(".txt")
    )
    print(f"Found {len(machines)} machines. Training GDNLite on each...")

    summary = {}
    t0 = time.time()
    for i, mid in enumerate(machines):
        t1 = time.time()
        res = train_one_machine(mid, verbose=False)
        score = res["score"]
        labels = res["labels"]
        raw_test = res["raw_test"]
        num_nodes = res["num_nodes"]

        threshold = float(np.percentile(score, 99))  # dynamic per-machine threshold
        threshold = max(threshold, 0.5)
        status = np.where(score >= threshold, "ANOMALY",
                           np.where(score >= threshold * 0.6, "WARNING", "NORMAL"))

        df = pd.DataFrame({
            "t": np.arange(len(score)),
            "score": np.round(score, 4),
            "true_label": labels,
            "status": status,
        })
        groups = np.array_split(np.arange(num_nodes), 4)
        for gname, grp in zip(GROUP_NAMES, groups):
            df[gname] = np.round(np.clip(raw_test[:, grp].mean(axis=1), 0, 1) * 100, 1)

        df.to_csv(os.path.join(RESULTS_DIR, f"{mid}.csv"), index=False)

        final_status = status[-1]
        summary[mid] = {
            "latest_score": float(score[-1]),
            "status": final_status,
            "threshold": threshold,
            "num_points": int(len(score)),
            "num_true_anomalies": int(labels.sum()),
            "num_nodes": int(num_nodes),
        }
        print(f"  ({i+1}/{len(machines)}) {mid}: status={final_status} "
              f"score={score[-1]:.3f} [{time.time()-t1:.1f}s]")

    with open(os.path.join(RESULTS_DIR, "summary.json"), "w") as f:
        json.dump(summary, f, indent=2)

    print(f"Done in {time.time()-t0:.1f}s. Results saved to {RESULTS_DIR}/")


if __name__ == "__main__":
    main()
