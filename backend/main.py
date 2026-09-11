"""
FastAPI backend for the GNN-Based Server Monitoring & Anomaly Detection system.
Serves precomputed GDNLite inference results (from train_and_infer.py) as a
live-playback API: each machine has an internal "cursor" that advances through
its historical test sequence, simulating real-time monitoring.

Run: uvicorn backend.main:app --reload --port 8000
Swagger UI: http://localhost:8000/docs
"""
import os
import json
from typing import Optional

import pandas as pd
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RESULTS_DIR = os.path.join(BASE_DIR, "results")

app = FastAPI(
    title="GNN Server Monitoring & Anomaly Detection API",
    description=(
        "Graph Neural Network-based anomaly detection over the SMD "
        "(Server Machine Dataset). Exposes live-playback endpoints for "
        "machine status, metrics, GNN anomaly scores, and alerts."
    ),
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------------------------------------------------------------- data cache

_machine_cache = {}
_cursors = {}


def load_machine_df(machine_id: str) -> pd.DataFrame:
    if machine_id not in _machine_cache:
        path = os.path.join(RESULTS_DIR, f"{machine_id}.csv")
        if not os.path.exists(path):
            raise HTTPException(status_code=404, detail=f"Unknown machine '{machine_id}'")
        _machine_cache[machine_id] = pd.read_csv(path)
        _cursors[machine_id] = 0
    return _machine_cache[machine_id]


def list_all_machines():
    with open(os.path.join(RESULTS_DIR, "summary.json")) as f:
        return json.load(f)


# ---------------------------------------------------------------- schemas

class MetricGroup(BaseModel):
    name: str
    value: float
    status: str


class MachineStatus(BaseModel):
    machine_id: str
    t: int
    status: str
    anomaly_score: float
    metrics: list[MetricGroup]


class Alert(BaseModel):
    machine_id: str
    severity: str
    message: str
    score: float
    t: int


# ---------------------------------------------------------------- helpers

def status_for_value(v: float) -> str:
    if v >= 70:
        return "WARNING" if v < 90 else "NORMAL"
    return "NORMAL"


def build_metric_groups(row) -> list[MetricGroup]:
    groups = []
    for name in ["CPU / Load", "Memory", "Disk", "Network"]:
        val = float(row[name])
        st = "NORMAL"
        if val > 85:
            st = "ANOMALY"
        elif val > 65:
            st = "WARNING"
        groups.append(MetricGroup(name=name, value=val, status=st))
    return groups


# ---------------------------------------------------------------- endpoints

@app.get("/", tags=["meta"])
def root():
    return {"message": "GNN Server Monitoring API is running.", "dashboard": "/dashboard", "docs": "/docs"}


@app.get("/machines", tags=["machines"])
def get_machines():
    """List all monitored machines with their latest known status."""
    return list_all_machines()


@app.get("/machines/{machine_id}/status", response_model=MachineStatus, tags=["machines"])
def get_machine_status(machine_id: str, advance: bool = True):
    """
    Return the current status snapshot for a machine, replaying its
    historical test sequence one step at a time (like a live feed).
    Set advance=false to peek without moving the cursor forward.
    """
    df = load_machine_df(machine_id)
    cursor = _cursors[machine_id]
    row = df.iloc[cursor]

    result = MachineStatus(
        machine_id=machine_id,
        t=int(row["t"]),
        status=row["status"],
        anomaly_score=float(row["score"]),
        metrics=build_metric_groups(row),
    )

    if advance:
        _cursors[machine_id] = (cursor + 1) % len(df)

    return result


@app.post("/machines/{machine_id}/reset", tags=["machines"])
def reset_cursor(machine_id: str):
    """Reset a machine's playback cursor back to timestep 0."""
    load_machine_df(machine_id)
    _cursors[machine_id] = 0
    return {"machine_id": machine_id, "cursor": 0}


@app.get("/machines/{machine_id}/history", tags=["machines"])
def get_machine_history(machine_id: str, window: int = 50):
    """Return the last `window` points up to the current cursor (for charts)."""
    df = load_machine_df(machine_id)
    cursor = _cursors[machine_id]
    start = max(0, cursor - window)
    sliced = df.iloc[start:cursor + 1]
    return {
        "machine_id": machine_id,
        "t": sliced["t"].tolist(),
        "score": sliced["score"].tolist(),
        "status": sliced["status"].tolist(),
    }


@app.get("/alerts", response_model=list[Alert], tags=["alerts"])
def get_alerts(min_severity: str = "WARNING"):
    """Return current alerts across all machines (status != NORMAL)."""
    summary = list_all_machines()
    severities = {"NORMAL": 0, "WARNING": 1, "ANOMALY": 2}
    threshold = severities.get(min_severity.upper(), 1)

    alerts = []
    for mid, info in summary.items():
        sev = severities.get(info["status"], 0)
        if sev >= threshold and threshold > 0:
            df = load_machine_df(mid)
            t = _cursors[mid]
            msg = (
                "Anomaly Detected — unusual behaviour in machine metrics."
                if info["status"] == "ANOMALY"
                else "Performance deviation detected."
            )
            alerts.append(Alert(
                machine_id=mid,
                severity=info["status"],
                message=msg,
                score=info["latest_score"],
                t=t,
            ))
    return alerts


@app.get("/overview", tags=["machines"])
def get_overview():
    """Aggregate counts used for the dashboard's Machine Overview card."""
    summary = list_all_machines()
    counts = {"NORMAL": 0, "WARNING": 0, "ANOMALY": 0}
    for info in summary.values():
        counts[info["status"]] = counts.get(info["status"], 0) + 1
    return {"counts": counts, "total_machines": len(summary)}


from fastapi.responses import HTMLResponse

@app.get("/dashboard", response_class=HTMLResponse, tags=["dashboard"])
def serve_dashboard():
    """Serves the complete interactive GNN monitoring dashboard."""
    try:
        from dashboard.render import get_dashboard_html
        return get_dashboard_html()
    except Exception as e:
        return f"<h1>Error loading dashboard: {e}</h1>"

