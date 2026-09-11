# GNN-Based Server Monitoring & Anomaly Detection System
### Multivariate Time-Series Anomaly Detection with PyTorch GDNLite, FastAPI & Streamlit

A production-grade, Graph Neural Network (GNN)-powered server infrastructure monitoring and anomaly detection system trained on the **Server Machine Dataset (SMD)**: 28 distributed cluster nodes across 38 multivariate hardware and network sensor metrics.

Includes a **FastAPI REST API (Swagger UI)** and an **interactive, pixel-perfect dark theme dashboard** featuring real-time simulation, sequence navigation, multi-metric sparklines, and deep-dive root-cause analysis for detected anomalies.

---

## 🚀 Quick Start in VS Code

### 1. Open in VS Code
1. Unzip `GNN_Server_Monitoring_Project_Working.zip`.
2. In VS Code, click **File -> Open Folder...** and select the unzipped `gnn_anomaly_project` folder.
3. Open a terminal in VS Code: Press `Ctrl + ~` (or go to **Terminal -> New Terminal**).

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Run the Streamlit Dashboard
In your VS Code terminal:
```bash
streamlit run dashboard/app.py
```
👉 Open your browser at: **http://localhost:8501**

### 4. (Optional) Run the FastAPI Backend
Open a second terminal in VS Code (`Ctrl + Shift + 5` or click `+` on the terminal tab):
```bash
uvicorn backend.main:app --reload --port 8000
```
- Interactive Web Dashboard: **http://localhost:8000/dashboard**
- API Documentation (Swagger UI): **http://localhost:8000/docs**

---

## 📁 Project Structure

```
gnn_anomaly_project/
├── backend/
│   ├── __init__.py
│   └── main.py                 # FastAPI backend with REST API & /dashboard endpoint
├── dashboard/
│   ├── app.py                  # Streamlit application entry point
│   └── render.py               # Interactive Single Page Application (SPA) renderer
├── models/
│   └── gnn_model.py            # PyTorch GDNLite (Graph Attention + GRU model)
├── results/
│   ├── bundle.json             # High-speed precomputed data cache for 0ms loads
│   ├── summary.json            # Anomaly statistics & status per machine
│   └── machine-*.csv           # Inference time-series data for all 28 machines
├── train_and_infer.py          # PyTorch training & inference pipeline
├── requirements.txt            # Python dependencies
└── README.md                   # Complete documentation
```

---

## 🧠 Model Architecture: GDNLite (Graph Deviation Network)

1. **Learnable Sensor Graph Topology**: Each of the 38 hardware/network sensors is assigned a continuous embedding vector. Cosine similarity between sensor embeddings constructs a dynamic top-k directed adjacency graph.
2. **Temporal Encoding**: A Gated Recurrent Unit (GRU) embeds historical sliding windows ($W = 10$) per sensor channel.
3. **Graph Attention Aggregation (GAT)**: Graph attention layers aggregate context from correlated neighbor sensors to forecast future sensor states.
4. **Anomaly Scoring**: Deviations between forecasted and observed ground-truth values are robustly normalized. Significant divergence across learned topological relationships triggers an anomaly flag (e.g. `machine-2-2` with critical score `1.00`).

---

## 🖥️ Dashboard Features

- **Sidebar Navigation**: Instant switching across Overview, Performance, Processes, Disk, Network, Machines, Alerts, and History tabs.
- **Sequence Switcher (1 to 28)**: Quickly inspect any cluster node with a single click.
- **⚡ Anomaly Root Cause Analysis ("View Analysis")**:
  - Multivariate sensor breakdown (CPU/Load, Memory, Disk, Network).
  - GNN Graph Attention breakdown report (`+4.82σ` deviation analysis).
  - High-resolution SVG incident timeline chart with highlighted anomaly zones.
  - Actionable remediation protocols (node isolation, lock inspection, buffer flush).
- **Real-Time Simulation**: Live ticking clock with smooth 2-second metric updates and Play/Pause controls.

---

## 📄 Resume Bullet Points (Ready to Copy-Paste!)

- **Server Monitoring & Anomaly Detection System using Graph Neural Networks (PyTorch, FastAPI, Streamlit)**
  - Engineered a multivariate time-series anomaly detection pipeline using a Graph Deviation Network (GDNLite) with GRU temporal encoders and Graph Attention Networks (GAT) trained on the Server Machine Dataset (SMD, 28 machines × 38 metrics).
  - Designed an interactive Single Page Application (SPA) dashboard in Streamlit & FastAPI featuring 0ms client-side routing, live telemetry simulation, and an automated Root-Cause Analysis (RCA) diagnostic engine.
  - Implemented high-throughput REST APIs using FastAPI with OpenAPI/Swagger documentation, replaying simulated cluster telemetry and real-time anomaly alerts.
