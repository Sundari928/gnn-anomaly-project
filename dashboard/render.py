"""
Builds the complete, reactive, interactive Single Page Application (SPA)
dashboard for the GNN-Based Server Monitoring & Anomaly Detection system.
"""
import os
import json

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RESULTS_DIR = os.path.join(BASE_DIR, "results")
BUNDLE_PATH = os.path.join(RESULTS_DIR, "bundle.json")


def load_bundle_data():
    if os.path.exists(BUNDLE_PATH):
        try:
            with open(BUNDLE_PATH, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass

    summary_path = os.path.join(RESULTS_DIR, "summary.json")
    if not os.path.exists(summary_path):
        return {"machines": {}, "machine_ids": [], "counts": {"NORMAL": 0, "WARNING": 0, "ANOMALY": 0}, "total_machines": 0}

    with open(summary_path, "r", encoding="utf-8") as f:
        summary = json.load(f)

    counts = {"NORMAL": 0, "WARNING": 0, "ANOMALY": 0}
    machines = {}
    for mid, info in summary.items():
        st = info.get("status", "NORMAL")
        counts[st] = counts.get(st, 0) + 1
        machines[mid] = {
            "id": mid,
            "status": st,
            "latest_score": round(float(info.get("latest_score", 0.0)), 3),
            "num_points": info.get("num_points", 0),
            "num_true_anomalies": info.get("num_true_anomalies", 0),
            "cpu": 20.0,
            "mem": 15.0,
            "disk": 12.0,
            "net": 10.0,
            "history": []
        }

    return {
        "machines": machines,
        "machine_ids": sorted(summary.keys()),
        "counts": counts,
        "total_machines": len(summary)
    }


def get_dashboard_html():
    bundle = load_bundle_data()
    bundle_json_str = json.dumps(bundle).replace("</", "<\\/")

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8"/>
<meta name="viewport" content="width=device-width, initial-scale=1.0"/>
<title>Server Monitoring & Anomaly Detection - GNN</title>
<style>
  :root {{
    --bg: #0a0e1a;
    --card-bg: #111a2e;
    --border: #1e293f;
    --border-light: #2d3b55;
    --text: #e8edf5;
    --muted: #8b93a7;
    --blue: #3b82f6;
    --blue-glow: rgba(59, 130, 246, 0.35);
    --blue-dk: #1d4ed8;
    --green: #22c55e;
    --amber: #f5a524;
    --red: #ef4444;
    --purple: #a855f7;
  }}
  * {{ box-sizing: border-box; margin: 0; padding: 0; }}
  body {{
    background: var(--bg);
    color: var(--text);
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif;
    user-select: none;
    -webkit-font-smoothing: antialiased;
    overflow-x: hidden;
  }}
  a {{ color: inherit; text-decoration: none; }}

  /* Top Bar */
  .topbar {{
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 16px 24px;
    border-bottom: 1px solid var(--border);
    background: #0d1322;
    position: sticky;
    top: 0;
    z-index: 50;
  }}
  .topbar-left {{ display: flex; align-items: center; gap: 14px; }}
  .logo-icon {{
    background: var(--blue);
    border-radius: 8px;
    width: 42px;
    height: 42px;
    display: flex;
    align-items: center;
    justify-content: center;
    flex-shrink: 0;
    box-shadow: 0 0 12px var(--blue-glow);
  }}
  .title {{ font-size: 19px; font-weight: 800; letter-spacing: 0.4px; color: #fff; }}
  .subtitle {{ font-size: 12.5px; color: var(--muted); margin-top: 2px; }}

  .topbar-center {{
    display: flex;
    align-items: center;
    gap: 12px;
    background: rgba(30, 41, 63, 0.6);
    padding: 6px 14px;
    border-radius: 20px;
    border: 1px solid var(--border);
    font-size: 12.5px;
  }}
  .sim-btn {{
    background: var(--blue);
    color: #fff;
    border: none;
    border-radius: 12px;
    padding: 4px 10px;
    font-size: 11.5px;
    font-weight: 700;
    cursor: pointer;
    transition: background 0.15s;
  }}
  .sim-btn:hover {{ background: var(--blue-dk); }}

  .topbar-right {{ display: flex; align-items: center; gap: 24px; }}
  .bell-wrap {{
    position: relative;
    cursor: pointer;
    padding: 6px;
    border-radius: 8px;
    transition: background 0.15s;
  }}
  .bell-wrap:hover {{ background: rgba(255,255,255,0.06); }}
  .badge {{
    position: absolute;
    top: -2px;
    right: -2px;
    background: var(--red);
    color: #fff;
    font-size: 10px;
    font-weight: 800;
    border-radius: 10px;
    padding: 1px 5px;
    box-shadow: 0 0 8px rgba(239, 68, 68, 0.6);
  }}
  .datetime {{ text-align: right; font-size: 13px; font-weight: 500; }}
  .running {{
    font-size: 11.5px;
    color: var(--green);
    margin-top: 3px;
    display: flex;
    align-items: center;
    justify-content: flex-end;
    gap: 5px;
  }}

  /* Layout Body */
  .layout-body {{ display: flex; align-items: stretch; min-height: calc(100vh - 75px); }}
  .sidebar {{
    width: 210px;
    flex-shrink: 0;
    border-right: 1px solid var(--border);
    padding: 16px 12px;
    display: flex;
    flex-direction: column;
    justify-content: space-between;
    background: #0b101c;
  }}
  .nav-item {{
    display: flex;
    align-items: center;
    gap: 12px;
    padding: 10px 14px;
    border-radius: 8px;
    color: var(--muted);
    font-size: 13.5px;
    font-weight: 500;
    margin-bottom: 4px;
    cursor: pointer;
    transition: all 0.15s ease;
    position: relative;
  }}
  .nav-item:hover {{ background: #141d33; color: var(--text); }}
  .nav-active {{ background: var(--blue) !important; color: #fff !important; font-weight: 700; box-shadow: 0 0 12px var(--blue-glow); }}
  .nav-badge {{
    position: absolute;
    right: 10px;
    background: var(--red);
    color: #fff;
    font-size: 10.5px;
    font-weight: 700;
    border-radius: 9px;
    padding: 1px 6px;
  }}
  .sidebar-footer {{
    display: flex;
    align-items: center;
    gap: 10px;
    padding: 14px 10px 0 10px;
    border-top: 1px solid var(--border);
  }}

  /* Content area */
  .content {{ flex: 1; padding: 22px 26px; overflow-y: auto; max-width: 100%; }}
  .tab-pane {{ display: none; }}
  .tab-pane.active {{ display: block; animation: fadeIn 0.2s ease-in-out; }}
  @keyframes fadeIn {{ from {{ opacity: 0; transform: translateY(4px); }} to {{ opacity: 1; transform: translateY(0); }} }}

  /* Cards & Utilities */
  .card {{
    background: var(--card-bg);
    border: 1px solid var(--border);
    border-radius: 12px;
    padding: 18px 20px;
    position: relative;
  }}
  .card-header {{ display: flex; justify-content: space-between; align-items: center; margin-bottom: 14px; }}
  .card-title {{ font-size: 13.5px; font-weight: 700; display: flex; align-items: center; gap: 8px; color: #fff; letter-spacing: 0.3px; }}
  .label {{ font-size: 11px; color: var(--muted); letter-spacing: 0.5px; text-transform: uppercase; font-weight: 600; }}
  .dot {{ display: inline-block; width: 8px; height: 8px; border-radius: 50%; margin-right: 6px; vertical-align: middle; }}
  .pulse-dot {{ animation: pulse 1.8s infinite; }}
  @keyframes pulse {{
    0% {{ box-shadow: 0 0 0 0 rgba(239, 68, 68, 0.7); }}
    70% {{ box-shadow: 0 0 0 8px rgba(239, 68, 68, 0); }}
    100% {{ box-shadow: 0 0 0 0 rgba(239, 68, 68, 0); }}
  }}
  .muted {{ color: var(--muted); }}

  /* Status Pills */
  .pill {{
    display: inline-flex;
    align-items: center;
    padding: 5px 14px;
    border-radius: 20px;
    font-weight: 700;
    font-size: 12px;
  }}
  .pill-NORMAL {{ background: rgba(34, 197, 94, 0.15); color: var(--green); }}
  .pill-WARNING {{ background: rgba(245, 165, 36, 0.15); color: var(--amber); }}
  .pill-ANOMALY {{ background: rgba(239, 68, 68, 0.18); color: var(--red); }}

  /* Buttons */
  .btn-analysis {{
    display: inline-flex;
    align-items: center;
    gap: 6px;
    background: linear-gradient(135deg, #ef4444, #b91c1c);
    color: #fff;
    border: none;
    border-radius: 8px;
    padding: 7px 14px;
    font-size: 12.5px;
    font-weight: 700;
    cursor: pointer;
    box-shadow: 0 2px 8px rgba(239, 68, 68, 0.35);
    transition: all 0.15s ease;
  }}
  .btn-analysis:hover {{
    background: linear-gradient(135deg, #f87171, #dc2626);
    transform: translateY(-1px);
    box-shadow: 0 4px 12px rgba(239, 68, 68, 0.5);
  }}
  .btn-secondary {{
    display: inline-flex;
    align-items: center;
    gap: 6px;
    background: #1e293f;
    color: var(--text);
    border: 1px solid var(--border-light);
    border-radius: 8px;
    padding: 6px 12px;
    font-size: 12px;
    font-weight: 600;
    cursor: pointer;
    transition: all 0.15s;
  }}
  .btn-secondary:hover {{ background: #283754; border-color: var(--blue); }}

  /* Current Machine Banner */
  .row1 {{ margin-bottom: 16px; }}
  .current-machine {{
    display: flex;
    align-items: center;
    gap: 16px;
    flex-wrap: wrap;
  }}
  .cm-icon {{
    background: var(--blue);
    border-radius: 8px;
    width: 40px;
    height: 40px;
    display: flex;
    align-items: center;
    justify-content: center;
    flex-shrink: 0;
  }}
  .cm-value {{ font-size: 20px; font-weight: 800; color: #fff; margin-top: 1px; }}
  .sequence {{
    display: flex;
    align-items: center;
    gap: 8px;
    font-size: 13px;
    margin-left: auto;
    flex: 1;
    min-width: 320px;
    justify-content: flex-end;
  }}
  .seq-scroll {{
    display: flex;
    gap: 5px;
    overflow-x: auto;
    padding: 3px 2px;
    max-width: 540px;
  }}
  .seq-dot {{
    display: inline-flex;
    align-items: center;
    justify-content: center;
    width: 28px;
    height: 28px;
    border-radius: 50%;
    background: #1c2740;
    color: var(--muted);
    font-size: 11.5px;
    font-weight: 700;
    cursor: pointer;
    flex-shrink: 0;
    transition: all 0.15s;
    border: 1px solid transparent;
  }}
  .seq-dot:hover {{ background: #2a3754; color: #fff; }}
  .seq-dot.seq-active {{ background: var(--blue); color: #fff; border-color: #60a5fa; box-shadow: 0 0 8px var(--blue-glow); }}
  .seq-dot.has-anomaly {{ border-color: var(--red); color: #fca5a5; }}

  /* Metric cards row */
  .metrics-row {{ display: grid; grid-template-columns: repeat(4, 1fr); gap: 16px; margin-bottom: 16px; }}
  .metric-card {{ padding: 16px 18px; }}
  .metric-top {{ display: flex; gap: 12px; margin-bottom: 10px; }}
  .metric-icon {{
    width: 38px;
    height: 38px;
    border-radius: 10px;
    display: flex;
    align-items: center;
    justify-content: center;
    flex-shrink: 0;
  }}
  .metric-value {{ font-size: 24px; font-weight: 800; margin: 2px 0; }}
  .status-line {{ font-size: 12.5px; font-weight: 600; display: flex; align-items: center; }}
  .sparkline {{ width: 100%; height: 50px; margin-top: 4px; }}

  /* Row 2 */
  .row2 {{ display: grid; grid-template-columns: 2.8fr 1.2fr; gap: 16px; margin-bottom: 16px; }}
  .live-card {{ min-height: 280px; }}
  .legend {{ font-size: 12px; color: var(--muted); display: flex; align-items: center; gap: 14px; }}
  .live-chart-wrap {{ display: flex; gap: 8px; height: 190px; margin-top: 8px; }}
  .y-axis {{
    display: flex;
    flex-direction: column;
    justify-content: space-between;
    font-size: 11px;
    color: var(--muted);
    padding: 8px 0 24px 0;
    width: 34px;
    text-align: right;
  }}
  .live-chart-svg {{ flex: 1; width: 100%; height: 100%; }}
  .time-caption {{ text-align: right; font-size: 11px; color: var(--muted); margin-top: 2px; }}

  /* Machine overview card */
  .overview-card .ov-row {{
    display: flex;
    align-items: center;
    font-size: 14px;
    padding: 10px 0;
    cursor: pointer;
    border-radius: 6px;
    transition: background 0.12s;
  }}
  .overview-card .ov-row:hover {{ background: rgba(255,255,255,0.03); }}
  .overview-card .ov-count {{ margin-left: auto; font-weight: 800; font-size: 16px; }}
  .overview-card hr {{ border: none; border-top: 1px solid var(--border); margin: 8px 0; }}

  /* Row 3 */
  .row3 {{ display: grid; grid-template-columns: 1fr 1.5fr 1.1fr; gap: 16px; margin-bottom: 16px; }}
  .gnn-body {{ display: flex; align-items: center; gap: 18px; margin-top: 10px; }}
  .donut-wrap {{ position: relative; width: 130px; height: 130px; flex-shrink: 0; }}
  .donut-label {{
    position: absolute;
    top: 50%;
    left: 50%;
    transform: translate(-50%, -50%);
    font-size: 24px;
    font-weight: 800;
    color: #fff;
    text-align: center;
  }}

  /* Table styling */
  .status-table {{ width: 100%; border-collapse: collapse; font-size: 13px; margin-top: 6px; }}
  .status-table th {{
    text-align: left;
    color: var(--muted);
    font-weight: 600;
    font-size: 11px;
    padding: 8px 8px;
    text-transform: uppercase;
    letter-spacing: 0.4px;
    border-bottom: 1px solid var(--border);
  }}
  .status-table td {{ padding: 10px 8px; border-top: 1px solid var(--border); vertical-align: middle; }}
  .status-table tr:hover td {{ background: rgba(59, 130, 246, 0.05); }}
  .row-highlight td {{ background: rgba(59, 130, 246, 0.12) !important; }}

  /* Alerts list */
  .alert-item {{
    padding: 10px 12px;
    border-radius: 6px;
    margin-bottom: 6px;
    background: #141d33;
    border-left: 3px solid var(--amber);
    transition: transform 0.12s;
  }}
  .alert-item:hover {{ transform: translateX(2px); }}
  .alert-item.severity-ANOMALY {{
    border-left-color: var(--red);
    background: rgba(239, 68, 68, 0.08);
  }}
  .alert-row {{ display: flex; justify-content: space-between; align-items: center; }}
  .alert-title {{ font-weight: 700; font-size: 13.5px; }}
  .alert-time {{ font-size: 11px; color: var(--muted); }}
  .alert-sub {{ font-size: 12px; color: var(--muted); margin-top: 3px; }}

  /* Machine Switcher Bar */
  .subnav {{
    display: flex;
    gap: 8px;
    margin-bottom: 16px;
    overflow-x: auto;
    padding-bottom: 6px;
  }}
  .subnav-btn {{
    padding: 7px 14px;
    border-radius: 8px;
    font-size: 12px;
    font-weight: 600;
    background: var(--card-bg);
    border: 1px solid var(--border);
    color: var(--muted);
    cursor: pointer;
    white-space: nowrap;
    transition: all 0.12s;
  }}
  .subnav-btn:hover {{ background: #1c2740; color: #fff; }}
  .subnav-btn.active {{ background: var(--blue); color: #fff; border-color: var(--blue); box-shadow: 0 0 8px var(--blue-glow); }}

  /* Machines Grid */
  .machine-grid {{ display: grid; grid-template-columns: repeat(auto-fill, minmax(220px, 1fr)); gap: 14px; }}
  .machine-tile {{
    background: var(--card-bg);
    border: 1px solid var(--border);
    border-radius: 10px;
    padding: 16px;
    cursor: pointer;
    transition: all 0.15s;
    position: relative;
  }}
  .machine-tile:hover {{
    border-color: var(--blue);
    transform: translateY(-2px);
    box-shadow: 0 6px 16px rgba(0,0,0,0.3);
  }}
  .machine-tile.active-tile {{ border-color: var(--blue); box-shadow: 0 0 10px var(--blue-glow); }}
  .mt-name {{ font-weight: 800; font-size: 14px; margin-bottom: 6px; display: flex; align-items: center; gap: 8px; }}
  .mt-score {{ font-size: 12px; color: var(--muted); margin-top: 6px; }}

  /* Modal Deep-Dive */
  .modal-overlay {{
    position: fixed;
    top: 0;
    left: 0;
    width: 100vw;
    height: 100vh;
    background: rgba(4, 7, 15, 0.85);
    backdrop-filter: blur(8px);
    z-index: 100;
    display: none;
    align-items: center;
    justify-content: center;
    padding: 20px;
  }}
  .modal-overlay.open {{ display: flex; animation: fadeIn 0.2s ease-out; }}
  .modal-card {{
    background: #0f172a;
    border: 1px solid var(--border-light);
    box-shadow: 0 20px 40px rgba(0,0,0,0.6), 0 0 24px rgba(239, 68, 68, 0.2);
    border-radius: 14px;
    width: 860px;
    max-width: 95vw;
    max-height: 90vh;
    overflow-y: auto;
    display: flex;
    flex-direction: column;
  }}
  .modal-header {{
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 18px 24px;
    border-bottom: 1px solid var(--border);
    background: #111e38;
  }}
  .modal-title-wrap {{ display: flex; align-items: center; gap: 12px; }}
  .modal-close {{
    background: rgba(255,255,255,0.06);
    border: 1px solid var(--border);
    color: var(--muted);
    border-radius: 8px;
    width: 32px;
    height: 32px;
    display: flex;
    align-items: center;
    justify-content: center;
    cursor: pointer;
    font-size: 16px;
    transition: all 0.15s;
  }}
  .modal-close:hover {{ background: rgba(239,68,68,0.2); color: var(--red); border-color: var(--red); }}
  .modal-body {{ padding: 22px 24px; }}
  .modal-section {{ margin-bottom: 20px; }}
  .modal-section-title {{
    font-size: 13px;
    font-weight: 700;
    color: var(--muted);
    text-transform: uppercase;
    letter-spacing: 0.5px;
    margin-bottom: 10px;
    display: flex;
    align-items: center;
    gap: 8px;
  }}
  .sensor-dev-grid {{ display: grid; grid-template-columns: repeat(4, 1fr); gap: 12px; margin-bottom: 16px; }}
  .dev-box {{
    background: #141f36;
    border: 1px solid var(--border);
    border-radius: 10px;
    padding: 12px;
    text-align: center;
  }}
  .dev-box.anomaly-box {{
    border-color: var(--red);
    background: rgba(239, 68, 68, 0.1);
  }}
  .dev-val {{ font-size: 20px; font-weight: 800; margin: 4px 0; }}
  .gnn-expl-box {{
    background: rgba(59, 130, 246, 0.08);
    border: 1px solid rgba(59, 130, 246, 0.25);
    border-radius: 10px;
    padding: 14px 16px;
    font-size: 13px;
    line-height: 1.6;
    margin-bottom: 16px;
  }}
  .remediation-list {{
    background: #131d33;
    border: 1px solid var(--border);
    border-radius: 10px;
    padding: 14px 18px;
    font-size: 13px;
    line-height: 1.7;
  }}
  .remediation-list li {{ margin-bottom: 6px; }}
</style>
</head>
<body>

<!-- Topbar -->
<div class="topbar">
  <div class="topbar-left">
    <div class="logo-icon">
      <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="#fff" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
        <rect x="2" y="3" width="20" height="7" rx="1.5"/><rect x="2" y="14" width="20" height="7" rx="1.5"/><line x1="6" y1="6.5" x2="6.01" y2="6.5"/><line x1="6" y1="17.5" x2="6.01" y2="17.5"/>
      </svg>
    </div>
    <div>
      <div class="title">SERVER MONITORING &amp; ANOMALY DETECTION</div>
      <div class="subtitle">GNN-Based Monitoring System (PyTorch GDNLite)</div>
    </div>
  </div>

  <div class="topbar-center">
    <span>Simulation: <strong id="simStatus">Live</strong></span>
    <button class="sim-btn" id="simToggleBtn" onclick="toggleSimulation()">⏸ Pause</button>
  </div>

  <div class="topbar-right">
    <div class="bell-wrap" onclick="setTab('Alerts')" title="View All Alerts">
      <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="#8b93a7" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
        <path d="M6 8a6 6 0 0 1 12 0c0 5 2 6 2 6H4s2-1 2-6"/><path d="M10 21a2 2 0 0 0 4 0"/>
      </svg>
      <span class="badge" id="bellBadge">12</span>
    </div>
    <div class="datetime">
      <div id="liveClock">Sep 11, 2026 &nbsp; 21:30:00</div>
      <div class="running"><span class="dot pulse-dot" style="background:var(--green)"></span>System Running</div>
    </div>
  </div>
</div>

<div class="layout-body">
  <!-- Sidebar -->
  <div class="sidebar">
    <nav>
      <div class="nav-item nav-active" data-tab="Overview" onclick="setTab('Overview')">
        <svg width="17" height="17" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M3 11.5 12 4l9 7.5"/><path d="M5 10v9a1 1 0 0 0 1 1h4v-6h4v6h4a1 1 0 0 0 1-1v-9"/></svg>
        <span>Overview</span>
      </div>
      <div class="nav-item" data-tab="Performance" onclick="setTab('Performance')">
        <svg width="17" height="17" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><line x1="4" y1="20" x2="4" y2="12"/><line x1="10" y1="20" x2="10" y2="6"/><line x1="16" y1="20" x2="16" y2="14"/><line x1="21" y1="20" x2="21" y2="9"/></svg>
        <span>Performance</span>
      </div>
      <div class="nav-item" data-tab="Processes" onclick="setTab('Processes')">
        <svg width="17" height="17" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><line x1="8" y1="6" x2="21" y2="6"/><line x1="8" y1="12" x2="21" y2="12"/><line x1="8" y1="18" x2="21" y2="18"/><line x1="3" y1="6" x2="3.01" y2="6"/><line x1="3" y1="12" x2="3.01" y2="12"/><line x1="3" y1="18" x2="3.01" y2="18"/></svg>
        <span>Processes</span>
      </div>
      <div class="nav-item" data-tab="Disk" onclick="setTab('Disk')">
        <svg width="17" height="17" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><ellipse cx="12" cy="5.5" rx="9" ry="3"/><path d="M3 5.5v13c0 1.66 4.03 3 9 3s9-1.34 9-3v-13"/><path d="M3 12c0 1.66 4.03 3 9 3s9-1.34 9-3"/></svg>
        <span>Disk</span>
      </div>
      <div class="nav-item" data-tab="Network" onclick="setTab('Network')">
        <svg width="17" height="17" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="9"/><line x1="3" y1="12" x2="21" y2="12"/><path d="M12 3c2.5 2.5 4 5.5 4 9s-1.5 6.5-4 9c-2.5-2.5-4-5.5-4-9s1.5-6.5 4-9z"/></svg>
        <span>Network</span>
      </div>
      <div class="nav-item" data-tab="Machines" onclick="setTab('Machines')">
        <svg width="17" height="17" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="2" y="3" width="20" height="7" rx="1.5"/><rect x="2" y="14" width="20" height="7" rx="1.5"/><line x1="6" y1="6.5" x2="6.01" y2="6.5"/><line x1="6" y1="17.5" x2="6.01" y2="17.5"/></svg>
        <span>Machines</span>
      </div>
      <div class="nav-item" data-tab="Alerts" onclick="setTab('Alerts')">
        <svg width="17" height="17" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M6 8a6 6 0 0 1 12 0c0 5 2 6 2 6H4s2-1 2-6"/><path d="M10 21a2 2 0 0 0 4 0"/></svg>
        <span>Alerts</span>
        <span class="nav-badge" id="navAlertBadge">12</span>
      </div>
      <div class="nav-item" data-tab="History" onclick="setTab('History')">
        <svg width="17" height="17" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="9"/><polyline points="12 7 12 12 15.5 14"/></svg>
        <span>History</span>
      </div>
    </nav>
    <div class="sidebar-footer">
      <span class="dot" style="background:var(--green)"></span>
      <div>
        <div style="font-weight:700;font-size:12.5px;">GNN GDNLite</div>
        <div class="muted" style="font-size:11px;">Attention: Online</div>
      </div>
    </div>
  </div>

  <!-- Content -->
  <div class="content">

    <!-- OVERVIEW TAB -->
    <div id="pane-Overview" class="tab-pane active">
      <div class="row1">
        <div class="card current-machine">
          <div class="cm-icon">
            <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="#fff" stroke-width="2">
              <rect x="2" y="3" width="20" height="7" rx="1.5"/><rect x="2" y="14" width="20" height="7" rx="1.5"/>
            </svg>
          </div>
          <div>
            <div class="label">CURRENT MACHINE</div>
            <div class="cm-value" id="cmName">machine-1-8</div>
          </div>
          <div id="cmPill" class="pill pill-NORMAL">
            <span class="dot" style="background:var(--green)"></span><span id="cmStatusText">NORMAL</span>
          </div>

          <button id="cmAnalysisBtn" class="btn-analysis" style="display:none;" onclick="openAnalysisModal(CURRENT_MACHINE)">
            ⚡ View Analysis
          </button>

          <div class="sequence">
            <span class="muted">Sequence:</span>
            <div class="seq-scroll" id="seqScroll"></div>
          </div>
        </div>
      </div>

      <!-- 4 Metric Cards -->
      <div class="metrics-row">
        <div class="card metric-card">
          <div class="metric-top">
            <div class="metric-icon" style="background:rgba(59,130,246,0.15)">
              <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="#3b82f6" stroke-width="2"><rect x="6" y="6" width="12" height="12" rx="1.5"/><rect x="9.5" y="9.5" width="5" height="5"/><line x1="9" y1="1" x2="9" y2="4"/><line x1="15" y1="1" x2="15" y2="4"/><line x1="9" y1="20" x2="9" y2="23"/><line x1="15" y1="20" x2="15" y2="23"/><line x1="1" y1="9" x2="4" y2="9"/><line x1="1" y1="15" x2="4" y2="15"/><line x1="20" y1="9" x2="23" y2="9"/><line x1="20" y1="15" x2="23" y2="15"/></svg>
            </div>
            <div>
              <div class="label">CPU / LOAD</div>
              <div class="metric-value" id="cardValCPU">20%</div>
              <div class="status-line" id="cardStCPU" style="color:var(--green)"><span class="dot" style="background:var(--green)"></span>Normal</div>
            </div>
          </div>
          <div class="sparkline" id="sparkCPU"></div>
        </div>

        <div class="card metric-card">
          <div class="metric-top">
            <div class="metric-icon" style="background:rgba(34,197,94,0.15)">
              <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="#22c55e" stroke-width="2"><rect x="3" y="7" width="18" height="10" rx="1.5"/><line x1="7" y1="7" x2="7" y2="17"/><line x1="11" y1="7" x2="11" y2="17"/><line x1="15" y1="7" x2="15" y2="17"/></svg>
            </div>
            <div>
              <div class="label">MEMORY</div>
              <div class="metric-value" id="cardValMEM">6%</div>
              <div class="status-line" id="cardStMEM" style="color:var(--green)"><span class="dot" style="background:var(--green)"></span>Normal</div>
            </div>
          </div>
          <div class="sparkline" id="sparkMEM"></div>
        </div>

        <div class="card metric-card">
          <div class="metric-top">
            <div class="metric-icon" style="background:rgba(168,85,247,0.15)">
              <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="#a855f7" stroke-width="2"><ellipse cx="12" cy="5.5" rx="9" ry="3"/><path d="M3 5.5v13c0 1.66 4.03 3 9 3s9-1.34 9-3v-13"/><path d="M3 12c0 1.66 4.03 3 9 3s9-1.34 9-3"/></svg>
            </div>
            <div>
              <div class="label">DISK</div>
              <div class="metric-value" id="cardValDISK">14%</div>
              <div class="status-line" id="cardStDISK" style="color:var(--green)"><span class="dot" style="background:var(--green)"></span>Normal</div>
            </div>
          </div>
          <div class="sparkline" id="sparkDISK"></div>
        </div>

        <div class="card metric-card">
          <div class="metric-top">
            <div class="metric-icon" style="background:rgba(245,165,36,0.15)">
              <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="#f5a524" stroke-width="2"><circle cx="12" cy="12" r="9"/><line x1="3" y1="12" x2="21" y2="12"/><path d="M12 3c2.5 2.5 4 5.5 4 9s-1.5 6.5-4 9c-2.5-2.5-4-5.5-4-9s1.5-6.5 4-9z"/></svg>
            </div>
            <div>
              <div class="label">NETWORK</div>
              <div class="metric-value" id="cardValNET">16%</div>
              <div class="status-line" id="cardStNET" style="color:var(--green)"><span class="dot" style="background:var(--green)"></span>Normal</div>
            </div>
          </div>
          <div class="sparkline" id="sparkNET"></div>
        </div>
      </div>

      <!-- Row 2: Live Monitoring & Machine Overview -->
      <div class="row2">
        <div class="card live-card">
          <div class="card-header">
            <div class="card-title">
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="#3b82f6" stroke-width="2"><line x1="4" y1="20" x2="4" y2="12"/><line x1="10" y1="20" x2="10" y2="6"/><line x1="16" y1="20" x2="16" y2="14"/><line x1="21" y1="20" x2="21" y2="9"/></svg>
              <span>LIVE MONITORING</span>
            </div>
            <div class="legend">
              <span><span class="dot" style="background:var(--green)"></span>Normal Pattern</span>
              <span><span class="dot" style="background:var(--red)"></span>Anomaly Point</span>
            </div>
          </div>
          <div class="live-chart-wrap">
            <div class="y-axis"><span>100%</span><span>50%</span><span>0%</span></div>
            <div class="live-chart-svg" id="liveChartContainer"></div>
          </div>
          <div class="time-caption">Time →</div>
        </div>

        <div class="card overview-card">
          <div class="card-title" style="margin-bottom:12px;">
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="#3b82f6" stroke-width="2"><rect x="2" y="3" width="20" height="7" rx="1.5"/><rect x="2" y="14" width="20" height="7" rx="1.5"/></svg>
            <span>MACHINE OVERVIEW</span>
          </div>
          <div class="ov-row" onclick="filterMachines('NORMAL')">
            <span><span class="dot" style="background:var(--green)"></span>Normal</span>
            <span class="ov-count" id="ovCountNormal">16</span>
          </div>
          <div class="ov-row" onclick="filterMachines('WARNING')">
            <span><span class="dot" style="background:var(--amber)"></span>Warning</span>
            <span class="ov-count" id="ovCountWarning">11</span>
          </div>
          <div class="ov-row" onclick="filterMachines('ANOMALY')" style="background:rgba(239,68,68,0.06);border-radius:6px;padding-left:6px;padding-right:6px;">
            <span><span class="dot pulse-dot" style="background:var(--red)"></span>Anomaly</span>
            <span class="ov-count" id="ovCountAnomaly" style="color:var(--red)">1</span>
          </div>
          <hr/>
          <div class="ov-row" onclick="filterMachines('ALL')">
            <span class="muted">Total Machines</span>
            <span class="ov-count" id="ovCountTotal">28</span>
          </div>
        </div>
      </div>

      <!-- Row 3: GNN Donut, Machine Status, Recent Alerts -->
      <div class="row3">
        <!-- GNN Donut -->
        <div class="card">
          <div class="card-title">
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="#3b82f6" stroke-width="2"><rect x="5" y="8" width="14" height="10" rx="2"/><circle cx="9" cy="13" r="1.2" fill="#3b82f6"/><circle cx="15" cy="13" r="1.2" fill="#3b82f6"/><line x1="12" y1="4" x2="12" y2="8"/></svg>
            <span>GNN ANOMALY SCORE</span>
          </div>
          <div class="gnn-body">
            <div class="donut-wrap">
              <div id="gnnDonutSvg"></div>
              <div class="donut-label" id="gnnScoreLabel">0.22</div>
            </div>
            <div>
              <div class="muted" style="font-size:11.5px;font-weight:600;">Status</div>
              <div class="status-line" id="gnnStatusText" style="font-size:15px;font-weight:800;margin-top:2px;">
                <span class="dot" style="background:var(--green)"></span>NORMAL
              </div>
              <div class="muted" id="gnnDescText" style="font-size:12px;margin-top:6px;line-height:1.4;">
                The current machine behavior is within the normal learned topological range.
              </div>
              <button class="btn-secondary" style="margin-top:10px;" onclick="openAnalysisModal(CURRENT_MACHINE)">
                🔍 View Detailed Analysis
              </button>
            </div>
          </div>
        </div>

        <!-- Recent Status Table -->
        <div class="card">
          <div class="card-title">
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="#3b82f6" stroke-width="2"><rect x="2" y="3" width="20" height="7" rx="1.5"/><rect x="2" y="14" width="20" height="7" rx="1.5"/></svg>
            <span>RECENT MACHINE STATUS</span>
          </div>
          <table class="status-table">
            <thead>
              <tr>
                <th>Machine</th>
                <th>Status</th>
                <th>Anomaly Score</th>
                <th>Action</th>
              </tr>
            </thead>
            <tbody id="recentStatusTbody"></tbody>
          </table>
        </div>

        <!-- Recent Alerts -->
        <div class="card">
          <div class="card-header">
            <div class="card-title">
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="#3b82f6" stroke-width="2"><path d="M6 8a6 6 0 0 1 12 0c0 5 2 6 2 6H4s2-1 2-6"/><path d="M10 21a2 2 0 0 0 4 0"/></svg>
              <span>RECENT ALERTS</span>
            </div>
            <span style="color:var(--blue);font-size:12px;font-weight:700;cursor:pointer;" onclick="setTab('Alerts')">View All →</span>
          </div>
          <div id="recentAlertsList"></div>
        </div>
      </div>
    </div>

    <!-- PERFORMANCE TAB -->
    <div id="pane-Performance" class="tab-pane">
      <div class="subnav" id="perfSubnav"></div>

      <div class="card" style="margin-bottom:16px;">
        <div style="display:flex;justify-content:space-between;align-items:center;">
          <div>
            <div class="card-title" style="font-size:16px;">
              PERFORMANCE &nbsp; <span class="muted" style="font-weight:500;">Machine: <strong id="perfMachineName">machine-1-8</strong></span>
            </div>
            <div class="muted" style="font-size:12px;margin-top:4px;">
              GNN Multivariate deviation tracking over 38-node sensor relationship graph.
            </div>
          </div>
          <div style="display:flex;align-items:center;gap:12px;">
            <div id="perfPill" class="pill pill-NORMAL"><span class="dot" style="background:var(--green)"></span>NORMAL</div>
            <button class="btn-analysis" onclick="openAnalysisModal(CURRENT_MACHINE)">⚡ View Analysis</button>
          </div>
        </div>
      </div>

      <div class="metrics-row" style="margin-bottom:16px;">
        <div class="card" style="text-align:center;padding:16px;">
          <div class="label">CPU / LOAD</div>
          <div class="metric-value" id="perfValCPU" style="color:var(--blue)">20%</div>
        </div>
        <div class="card" style="text-align:center;padding:16px;">
          <div class="label">MEMORY</div>
          <div class="metric-value" id="perfValMEM" style="color:var(--green)">6%</div>
        </div>
        <div class="card" style="text-align:center;padding:16px;">
          <div class="label">DISK</div>
          <div class="metric-value" id="perfValDISK" style="color:var(--purple)">14%</div>
        </div>
        <div class="card" style="text-align:center;padding:16px;">
          <div class="label">NETWORK</div>
          <div class="metric-value" id="perfValNET" style="color:var(--amber)">16%</div>
        </div>
      </div>

      <div class="card" style="margin-bottom:16px;">
        <div class="card-header">
          <div class="card-title">PERFORMANCE &amp; ANOMALY TIMELINE GRAPH</div>
          <div class="legend">
            <span><span class="dot" style="background:var(--blue)"></span>Anomaly Score %</span>
            <span><span class="dot" style="background:var(--red)"></span>Anomaly Detected</span>
          </div>
        </div>
        <div style="height:260px;" id="perfBigChart"></div>
      </div>

      <div class="card">
        <div style="font-size:13.5px;line-height:2;">
          <b>Current GNN Anomaly Score:</b> <span id="perfScoreText">0.22</span> &nbsp;
          <span class="dot" id="perfScoreDot" style="background:var(--green)"></span>
          <span id="perfScoreStatus" style="color:var(--green);font-weight:700;">NORMAL</span><br/>
          <b>Ground-truth anomalies in test set:</b> <span id="perfGroundTruth">763</span> / <span id="perfTotalPoints">23689</span> points<br/>
          <b>GNN Model Architecture:</b> GDNLite with learnable node embeddings + GRU sensor encoding + Graph Attention Layer (GAT)
        </div>
      </div>
    </div>

    <!-- PROCESSES TAB -->
    <div id="pane-Processes" class="tab-pane">
      <div class="card">
        <div class="card-title" style="font-size:16px;margin-bottom:4px;">
          <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="#3b82f6" stroke-width="2"><line x1="8" y1="6" x2="21" y2="6"/><line x1="8" y1="12" x2="21" y2="12"/><line x1="8" y1="18" x2="21" y2="18"/><line x1="3" y1="6" x2="3.01" y2="6"/><line x1="3" y1="12" x2="3.01" y2="12"/><line x1="3" y1="18" x2="3.01" y2="18"/></svg>
          <span>PROCESSES &amp; RESOURCE ALLOCATION</span>
        </div>
        <div class="muted" style="font-size:12.5px;margin-bottom:14px;">
          Resource-group telemetry across all 28 monitored machines (38 sensors aggregated into 4 primary groups).
        </div>
        <table class="status-table">
          <thead>
            <tr>
              <th>Machine</th>
              <th>CPU / Load</th>
              <th>Memory</th>
              <th>Disk</th>
              <th>Network</th>
              <th>Status</th>
              <th>Action</th>
            </tr>
          </thead>
          <tbody id="processesTbody"></tbody>
        </table>
      </div>
    </div>

    <!-- DISK TAB -->
    <div id="pane-Disk" class="tab-pane">
      <div class="subnav" id="diskSubnav"></div>
      <div class="card" style="margin-bottom:16px;">
        <div class="card-header">
          <div class="card-title" style="font-size:16px;">
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="#a855f7" stroke-width="2"><ellipse cx="12" cy="5.5" rx="9" ry="3"/><path d="M3 5.5v13c0 1.66 4.03 3 9 3s9-1.34 9-3v-13"/></svg>
            <span>DISK I/O UTILIZATION &nbsp; <span class="muted" style="font-weight:500;">Machine: <strong id="diskMachineName">machine-1-8</strong></span></span>
          </div>
          <div class="metric-value" id="diskCurrentVal" style="color:var(--purple)">14%</div>
        </div>
        <div style="height:220px;" id="diskBigChart"></div>
      </div>
      <div class="card">
        <div class="card-title" style="margin-bottom:10px;">DISK ACTIVITY RANKING (ALL MACHINES)</div>
        <table class="status-table">
          <thead><tr><th>Machine</th><th>Disk Utilization</th><th>Usage %</th><th>Action</th></tr></thead>
          <tbody id="diskRankTbody"></tbody>
        </table>
      </div>
    </div>

    <!-- NETWORK TAB -->
    <div id="pane-Network" class="tab-pane">
      <div class="subnav" id="netSubnav"></div>
      <div class="card" style="margin-bottom:16px;">
        <div class="card-header">
          <div class="card-title" style="font-size:16px;">
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="#f5a524" stroke-width="2"><circle cx="12" cy="12" r="9"/><line x1="3" y1="12" x2="21" y2="12"/></svg>
            <span>NETWORK BANDWIDTH &amp; THROUGHPUT &nbsp; <span class="muted" style="font-weight:500;">Machine: <strong id="netMachineName">machine-1-8</strong></span></span>
          </div>
          <div class="metric-value" id="netCurrentVal" style="color:var(--amber)">16%</div>
        </div>
        <div style="height:220px;" id="netBigChart"></div>
      </div>
      <div class="card">
        <div class="card-title" style="margin-bottom:10px;">NETWORK THROUGHPUT RANKING (ALL MACHINES)</div>
        <table class="status-table">
          <thead><tr><th>Machine</th><th>Network Traffic</th><th>Throughput %</th><th>Action</th></tr></thead>
          <tbody id="netRankTbody"></tbody>
        </table>
      </div>
    </div>

    <!-- MACHINES TAB -->
    <div id="pane-Machines" class="tab-pane">
      <div class="card" style="margin-bottom:16px;">
        <div style="display:flex;justify-content:space-between;align-items:center;flex-wrap:wrap;gap:12px;">
          <div>
            <div class="card-title" style="font-size:16px;">
              <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="#3b82f6" stroke-width="2"><rect x="2" y="3" width="20" height="7" rx="1.5"/><rect x="2" y="14" width="20" height="7" rx="1.5"/></svg>
              <span>ALL MONITORED MACHINES</span>
            </div>
            <div class="muted" style="font-size:12px;margin-top:4px;">28 cluster nodes actively monitored via Graph Neural Network</div>
          </div>
          <div style="display:flex;gap:8px;">
            <button class="btn-secondary" onclick="filterMachines('ALL')">All (28)</button>
            <button class="btn-secondary" style="border-color:var(--red);color:#fca5a5;" onclick="filterMachines('ANOMALY')">Anomalies (1)</button>
            <button class="btn-secondary" style="border-color:var(--amber);color:#fde68a;" onclick="filterMachines('WARNING')">Warnings (11)</button>
            <button class="btn-secondary" style="border-color:var(--green);color:#86efac;" onclick="filterMachines('NORMAL')">Normal (16)</button>
          </div>
        </div>
      </div>
      <div class="machine-grid" id="machinesGrid"></div>
    </div>

    <!-- ALERTS TAB -->
    <div id="pane-Alerts" class="tab-pane">
      <div class="card" style="margin-bottom:16px;">
        <div style="display:flex;justify-content:space-between;align-items:center;">
          <div>
            <div class="card-title" style="font-size:16px;">
              <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="#ef4444" stroke-width="2"><path d="M6 8a6 6 0 0 1 12 0c0 5 2 6 2 6H4s2-1 2-6"/><path d="M10 21a2 2 0 0 0 4 0"/></svg>
              <span>INCIDENT QUEUE &amp; ACTIVE ALERTS</span>
            </div>
            <div class="muted" style="font-size:12px;margin-top:4px;">Machines exhibiting statistical or topological deviation from normal baseline.</div>
          </div>
          <div style="display:flex;gap:8px;">
            <button class="btn-secondary" onclick="filterAlerts('ALL')">All Alerts (12)</button>
            <button class="btn-secondary" style="border-color:var(--red);color:#fca5a5;" onclick="filterAlerts('ANOMALY')">Critical Only (1)</button>
            <button class="btn-secondary" style="border-color:var(--amber);color:#fde68a;" onclick="filterAlerts('WARNING')">Warnings (11)</button>
          </div>
        </div>
      </div>
      <div class="card">
        <div id="fullAlertsList"></div>
      </div>
    </div>

    <!-- HISTORY TAB -->
    <div id="pane-History" class="tab-pane">
      <div class="card">
        <div class="card-title" style="font-size:16px;margin-bottom:4px;">
          <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="#3b82f6" stroke-width="2"><circle cx="12" cy="12" r="9"/><polyline points="12 7 12 12 15.5 14"/></svg>
          <span>HISTORICAL BENCHMARK &amp; SMD GROUND-TRUTH</span>
        </div>
        <div class="muted" style="font-size:12.5px;margin-bottom:14px;">
          Ground-truth anomaly evaluation metrics per machine on the ServerMachineDataset (SMD).
        </div>
        <table class="status-table">
          <thead>
            <tr>
              <th>Machine</th>
              <th>Test Points</th>
              <th>True Anomalies</th>
              <th>Anomaly Rate %</th>
              <th>GNN Status</th>
              <th>Action</th>
            </tr>
          </thead>
          <tbody id="historyTbody"></tbody>
        </table>
      </div>
    </div>

  </div>
</div>

<!-- ANOMALY DEEP-DIVE MODAL -->
<div id="analysisModal" class="modal-overlay" onclick="handleModalOverlayClick(event)">
  <div class="modal-card">
    <div class="modal-header">
      <div class="modal-title-wrap">
        <div class="metric-icon" style="background:rgba(239,68,68,0.2);">
          <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="#ef4444" stroke-width="2.5"><circle cx="12" cy="12" r="10"/><line x1="12" y1="8" x2="12" y2="12"/><line x1="12" y1="16" x2="12.01" y2="16"/></svg>
        </div>
        <div>
          <div style="font-size:16px;font-weight:800;color:#fff;">ANOMALY ROOT-CAUSE ANALYSIS</div>
          <div class="muted" style="font-size:12px;">Machine: <strong id="modalMid" style="color:#fff;">machine-2-2</strong> &nbsp;•&nbsp; GNN GDNLite Attention Engine</div>
        </div>
      </div>
      <div style="display:flex;align-items:center;gap:12px;">
        <span id="modalSeverityBadge" class="pill pill-ANOMALY">CRITICAL ANOMALY</span>
        <button class="modal-close" onclick="closeAnalysisModal()">✕</button>
      </div>
    </div>

    <div class="modal-body">
      <!-- Section 1: Sensor breakdown -->
      <div class="modal-section">
        <div class="modal-section-title">
          <span>1. MULTIVARIATE SENSOR GROUP DEVIATIONS</span>
        </div>
        <div class="sensor-dev-grid">
          <div class="dev-box" id="devBoxCPU">
            <div class="label">CPU / LOAD</div>
            <div class="dev-val" id="modalValCPU">10.1%</div>
            <div class="muted" style="font-size:11px;" id="modalDevCPU">Baseline: Normal</div>
          </div>
          <div class="dev-box" id="devBoxMEM">
            <div class="label">MEMORY</div>
            <div class="dev-val" id="modalValMEM">17.1%</div>
            <div class="muted" style="font-size:11px;" id="modalDevMEM">Baseline: Normal</div>
          </div>
          <div class="dev-box" id="devBoxDISK">
            <div class="label">DISK</div>
            <div class="dev-val" id="modalValDISK">1.8%</div>
            <div class="muted" style="font-size:11px;" id="modalDevDISK">Baseline: Normal</div>
          </div>
          <div class="dev-box" id="devBoxNET">
            <div class="label">NETWORK</div>
            <div class="dev-val" id="modalValNET">6.9%</div>
            <div class="muted" style="font-size:11px;" id="modalDevNET">Baseline: Normal</div>
          </div>
        </div>
      </div>

      <!-- Section 2: GNN Diagnosis -->
      <div class="modal-section">
        <div class="modal-section-title">
          <span>2. GRAPH DEVIATION NETWORK (GDN) TOPOLOGY DIAGNOSTICS</span>
        </div>
        <div class="gnn-expl-box" id="modalGnnExpl">
          <strong>GNN Attention Disruption Detected:</strong> The learned graph attention weights across the 38 sensor nodes showed a high-magnitude cosine distance divergence. Specifically, pairwise inter-node correlation between sensor clusters [12, 17, 31] collapsed, exceeding the standard deviation threshold by <strong>+4.82σ</strong>.
        </div>
      </div>

      <!-- Section 3: Anomaly Timeline Chart -->
      <div class="modal-section">
        <div class="modal-section-title">
          <span>3. INCIDENT TIMELINE &amp; ANOMALY POINT</span>
        </div>
        <div class="card" style="padding:12px;background:#0d1527;">
          <div style="height:180px;" id="modalTimelineChart"></div>
        </div>
      </div>

      <!-- Section 4: Recommended Remediation -->
      <div class="modal-section">
        <div class="modal-section-title">
          <span>4. RECOMMENDED REMEDIATION ACTIONS</span>
        </div>
        <ul class="remediation-list" id="modalRemediation">
          <li><strong>Cluster Isolation:</strong> Temporarily remove node from reverse-proxy/load balancer pool.</li>
          <li><strong>Thread &amp; Process Inspection:</strong> Inspect runaway worker processes causing lock contention.</li>
          <li><strong>I/O Flush Check:</strong> Check dirty write buffer and swap paging activity on root mount.</li>
          <li><strong>Re-convergence Verification:</strong> Run telemetry health sweep until GNN anomaly score drops below 0.35 threshold.</li>
        </ul>
      </div>

      <div style="display:flex;justify-content:flex-end;gap:12px;margin-top:10px;">
        <button class="btn-secondary" onclick="closeAnalysisModal()">Close</button>
        <button class="btn-analysis" style="background:var(--blue);" onclick="closeAnalysisModal(); setTab('Performance'); selectMachine(CURRENT_MACHINE);">
          View Machine in Performance →
        </button>
      </div>
    </div>
  </div>
</div>

<script>
const DATA_BUNDLE = {bundle_json_str};

let CURRENT_TAB = "Overview";
let CURRENT_MACHINE = "machine-1-8";
let SIMULATION_RUNNING = true;
let simInterval = null;
let machineFilter = "ALL";
let alertFilter = "ALL";

window.addEventListener("DOMContentLoaded", () => {{
  if (!DATA_BUNDLE.machines[CURRENT_MACHINE]) {{
    CURRENT_MACHINE = DATA_BUNDLE.machine_ids[0] || "machine-1-1";
  }}

  initClock();
  renderSequenceDots();
  renderSubnavs();
  updateMachineOverviewStats();
  renderOverview(CURRENT_MACHINE);
  renderProcessesTable();
  renderMachinesGrid();
  renderAlertsList();
  renderHistoryTable();

  startSimulation();
}});

function setTab(tabName) {{
  CURRENT_TAB = tabName;
  document.querySelectorAll(".nav-item").forEach(el => {{
    el.classList.toggle("nav-active", el.getAttribute("data-tab") === tabName);
  }});
  document.querySelectorAll(".tab-pane").forEach(pane => {{
    pane.classList.toggle("active", pane.id === "pane-" + tabName);
  }});

  if (tabName === "Performance") {{
    renderPerformance(CURRENT_MACHINE);
  }} else if (tabName === "Disk") {{
    renderDisk(CURRENT_MACHINE);
  }} else if (tabName === "Network") {{
    renderNetwork(CURRENT_MACHINE);
  }} else if (tabName === "Machines") {{
    renderMachinesGrid();
  }} else if (tabName === "Alerts") {{
    renderAlertsList();
  }} else if (tabName === "Overview") {{
    renderOverview(CURRENT_MACHINE);
  }}

  window.scrollTo({{ top: 0, behavior: "smooth" }});
}}

function selectMachine(mid) {{
  if (!DATA_BUNDLE.machines[mid]) return;
  CURRENT_MACHINE = mid;

  document.querySelectorAll(".seq-dot").forEach(dot => {{
    dot.classList.toggle("seq-active", dot.getAttribute("data-mid") === mid);
  }});
  document.querySelectorAll(".subnav-btn").forEach(btn => {{
    btn.classList.toggle("active", btn.getAttribute("data-mid") === mid);
  }});

  renderOverview(CURRENT_MACHINE);
  if (CURRENT_TAB === "Performance") renderPerformance(CURRENT_MACHINE);
  if (CURRENT_TAB === "Disk") renderDisk(CURRENT_MACHINE);
  if (CURRENT_TAB === "Network") renderNetwork(CURRENT_MACHINE);
}}

function renderSequenceDots() {{
  const container = document.getElementById("seqScroll");
  container.innerHTML = "";
  DATA_BUNDLE.machine_ids.forEach((mid, idx) => {{
    const info = DATA_BUNDLE.machines[mid];
    const dot = document.createElement("div");
    dot.className = "seq-dot" + (mid === CURRENT_MACHINE ? " seq-active" : "") + (info.status === "ANOMALY" ? " has-anomaly" : "");
    dot.setAttribute("data-mid", mid);
    dot.innerText = idx + 1;
    dot.title = mid + " (" + info.status + " - Score: " + info.latest_score + ")";
    dot.onclick = () => selectMachine(mid);
    container.appendChild(dot);
  }});
}}

function renderSubnavs() {{
  ["perfSubnav", "diskSubnav", "netSubnav"].forEach(id => {{
    const el = document.getElementById(id);
    if (!el) return;
    el.innerHTML = "";
    DATA_BUNDLE.machine_ids.forEach(mid => {{
      const btn = document.createElement("button");
      btn.className = "subnav-btn" + (mid === CURRENT_MACHINE ? " active" : "");
      btn.setAttribute("data-mid", mid);
      const st = DATA_BUNDLE.machines[mid].status;
      const dotColor = st === "ANOMALY" ? "var(--red)" : (st === "WARNING" ? "var(--amber)" : "var(--green)");
      btn.innerHTML = `<span class="dot" style="background:${{dotColor}}"></span>` + mid;
      btn.onclick = () => selectMachine(mid);
      el.appendChild(btn);
    }});
  }});
}}

function renderOverview(mid) {{
  const m = DATA_BUNDLE.machines[mid];
  if (!m) return;

  document.getElementById("cmName").innerText = m.id;
  const pill = document.getElementById("cmPill");
  pill.className = "pill pill-" + m.status;
  const stColor = m.status === "ANOMALY" ? "var(--red)" : (m.status === "WARNING" ? "var(--amber)" : "var(--green)");
  pill.innerHTML = `<span class="dot" style="background:${{stColor}}"></span><span>${{m.status}}</span>`;

  const analysisBtn = document.getElementById("cmAnalysisBtn");
  if (m.status === "ANOMALY" || m.status === "WARNING" || m.latest_score > 0.6) {{
    analysisBtn.style.display = "inline-flex";
    analysisBtn.innerHTML = (m.status === "ANOMALY" ? "⚡ Analyze Anomaly" : "🔍 View Analysis");
  }} else {{
    analysisBtn.style.display = "none";
  }}

  document.getElementById("cardValCPU").innerText = m.cpu.toFixed(0) + "%";
  document.getElementById("cardValMEM").innerText = m.mem.toFixed(0) + "%";
  document.getElementById("cardValDISK").innerText = m.disk.toFixed(0) + "%";
  document.getElementById("cardValNET").innerText = m.net.toFixed(0) + "%";

  updateMetricStatus("cardStCPU", m.cpu, 65, 85);
  updateMetricStatus("cardStMEM", m.mem, 70, 88);
  updateMetricStatus("cardStDISK", m.disk, 75, 90);
  updateMetricStatus("cardStNET", m.net, 70, 88);

  const hist = m.history || [];
  renderSparkline("sparkCPU", hist.map(h => h.cpu), "#3b82f6");
  renderSparkline("sparkMEM", hist.map(h => h.mem), "#22c55e");
  renderSparkline("sparkDISK", hist.map(h => h.disk), "#a855f7");
  renderSparkline("sparkNET", hist.map(h => h.net), "#f5a524");

  renderLiveMonitoringChart("liveChartContainer", hist);

  renderDonut("gnnDonutSvg", m.latest_score, stColor);
  document.getElementById("gnnScoreLabel").innerText = m.latest_score.toFixed(2);
  const gnnSt = document.getElementById("gnnStatusText");
  gnnSt.style.color = stColor;
  gnnSt.innerHTML = `<span class="dot" style="background:${{stColor}}"></span>` + m.status;

  const desc = {{
    "NORMAL": "The current machine behavior is within the normal learned topological range.",
    "WARNING": "Graph Deviation Network detected mild metric divergence from cluster baseline.",
    "ANOMALY": "Critical Anomaly Detected! Cross-sensor correlation failure detected by GNN."
  }}[m.status] || "Monitored node operating normally.";
  document.getElementById("gnnDescText").innerText = desc;

  renderRecentStatusTable();
  renderRecentAlerts();
}}

function updateMetricStatus(elemId, val, warnThresh, anomThresh) {{
  const el = document.getElementById(elemId);
  if (!el) return;
  if (val >= anomThresh) {{
    el.style.color = "var(--red)";
    el.innerHTML = `<span class="dot" style="background:var(--red)"></span>Anomaly`;
  }} else if (val >= warnThresh) {{
    el.style.color = "var(--amber)";
    el.innerHTML = `<span class="dot" style="background:var(--amber)"></span>Warning`;
  }} else {{
    el.style.color = "var(--green)";
    el.innerHTML = `<span class="dot" style="background:var(--green)"></span>Normal`;
  }}
}}

function updateMachineOverviewStats() {{
  document.getElementById("ovCountNormal").innerText = DATA_BUNDLE.counts.NORMAL || 0;
  document.getElementById("ovCountWarning").innerText = DATA_BUNDLE.counts.WARNING || 0;
  document.getElementById("ovCountAnomaly").innerText = DATA_BUNDLE.counts.ANOMALY || 0;
  document.getElementById("ovCountTotal").innerText = DATA_BUNDLE.total_machines || 0;

  const alertCount = (DATA_BUNDLE.counts.ANOMALY || 0) + (DATA_BUNDLE.counts.WARNING || 0);
  document.getElementById("bellBadge").innerText = alertCount;
  document.getElementById("navAlertBadge").innerText = alertCount;
}}

function renderRecentStatusTable() {{
  const tbody = document.getElementById("recentStatusTbody");
  tbody.innerHTML = "";

  const visible = ["machine-2-2", "machine-1-1", "machine-1-3", "machine-1-8", "machine-1-6", "machine-2-8"];
  if (!visible.includes(CURRENT_MACHINE)) visible.unshift(CURRENT_MACHINE);

  visible.slice(0, 6).forEach(mid => {{
    const m = DATA_BUNDLE.machines[mid];
    if (!m) return;
    const isAct = mid === CURRENT_MACHINE;
    const stColor = m.status === "ANOMALY" ? "var(--red)" : (m.status === "WARNING" ? "var(--amber)" : "var(--green)");

    const tr = document.createElement("tr");
    if (isAct) tr.className = "row-highlight";
    tr.innerHTML = `
      <td style="font-weight:700;cursor:pointer;" onclick="selectMachine('${{mid}}')">${{mid}}</td>
      <td><span class="dot" style="background:${{stColor}}"></span><span style="color:${{stColor}}">${{m.status}}</span></td>
      <td style="color:${{m.status !== 'NORMAL' ? stColor : 'inherit'}};font-weight:600;">${{m.latest_score.toFixed(2)}}</td>
      <td>
        <button class="${{m.status === 'ANOMALY' ? 'btn-analysis' : 'btn-secondary'}}" style="padding:4px 8px;font-size:11px;" onclick="openAnalysisModal('${{mid}}')">
          ${{m.status === 'ANOMALY' ? '⚡ Analyze' : 'View'}}
        </button>
      </td>
    `;
    tbody.appendChild(tr);
  }});
}}

function renderRecentAlerts() {{
  const list = document.getElementById("recentAlertsList");
  list.innerHTML = "";

  const alertMids = DATA_BUNDLE.machine_ids.filter(mid => DATA_BUNDLE.machines[mid].status !== "NORMAL");
  alertMids.sort((a, b) => (DATA_BUNDLE.machines[b].status === "ANOMALY" ? 1 : 0) - (DATA_BUNDLE.machines[a].status === "ANOMALY" ? 1 : 0));

  alertMids.slice(0, 4).forEach(mid => {{
    const m = DATA_BUNDLE.machines[mid];
    const isAnom = m.status === "ANOMALY";
    const item = document.createElement("div");
    item.className = "alert-item severity-" + m.status;
    item.innerHTML = `
      <div class="alert-row">
        <span class="alert-title" style="color:${{isAnom ? 'var(--red)' : '#fff'}}">${{m.id}}</span>
        <span class="alert-time">Score: ${{m.latest_score.toFixed(2)}}</span>
      </div>
      <div class="alert-sub">${{isAnom ? 'Unusual behaviour in multivariate telemetry. Critical anomaly detected.' : 'Performance deviation detected.'}}</div>
      <div style="margin-top:6px;display:flex;justify-content:flex-end;">
        <button class="${{isAnom ? 'btn-analysis' : 'btn-secondary'}}" style="padding:3px 8px;font-size:11px;" onclick="openAnalysisModal('${{mid}}')">
          ${{isAnom ? '⚡ View Analysis →' : 'Inspect'}}
        </button>
      </div>
    `;
    list.appendChild(item);
  }});
}}

function renderProcessesTable() {{
  const tbody = document.getElementById("processesTbody");
  tbody.innerHTML = "";

  DATA_BUNDLE.machine_ids.forEach(mid => {{
    const m = DATA_BUNDLE.machines[mid];
    const stColor = m.status === "ANOMALY" ? "var(--red)" : (m.status === "WARNING" ? "var(--amber)" : "var(--green)");

    const tr = document.createElement("tr");
    tr.innerHTML = `
      <td style="font-weight:700;cursor:pointer;" onclick="selectMachine('${{mid}}'); setTab('Performance');">${{mid}}</td>
      <td>${{m.cpu.toFixed(0)}}%</td>
      <td>${{m.mem.toFixed(0)}}%</td>
      <td>${{m.disk.toFixed(0)}}%</td>
      <td>${{m.net.toFixed(0)}}%</td>
      <td><span class="dot" style="background:${{stColor}}"></span><span style="color:${{stColor}}">${{m.status}}</span></td>
      <td>
        <button class="${{m.status === 'ANOMALY' ? 'btn-analysis' : 'btn-secondary'}}" style="padding:4px 8px;font-size:11.5px;" onclick="openAnalysisModal('${{mid}}')">
          ${{m.status === 'ANOMALY' ? '⚡ Analyze' : 'Inspect'}}
        </button>
      </td>
    `;
    tbody.appendChild(tr);
  }});
}}

function renderMachinesGrid() {{
  const grid = document.getElementById("machinesGrid");
  grid.innerHTML = "";

  let list = DATA_BUNDLE.machine_ids;
  if (machineFilter !== "ALL") {{
    list = list.filter(mid => DATA_BUNDLE.machines[mid].status === machineFilter);
  }}

  list.forEach(mid => {{
    const m = DATA_BUNDLE.machines[mid];
    const stColor = m.status === "ANOMALY" ? "var(--red)" : (m.status === "WARNING" ? "var(--amber)" : "var(--green)");

    const tile = document.createElement("div");
    tile.className = "machine-tile" + (mid === CURRENT_MACHINE ? " active-tile" : "");
    tile.innerHTML = `
      <div class="mt-name" style="color:#fff;">
        <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="${{stColor}}" stroke-width="2"><rect x="2" y="3" width="20" height="7" rx="1.5"/><rect x="2" y="14" width="20" height="7" rx="1.5"/></svg>
        <span>${{mid}}</span>
      </div>
      <div class="status-line" style="color:${{stColor}};margin-bottom:6px;">
        <span class="dot" style="background:${{stColor}}"></span>${{m.status}}
      </div>
      <div class="mt-score">GNN Score: <strong>${{m.latest_score.toFixed(2)}}</strong></div>
      <div style="margin-top:12px;display:flex;gap:6px;">
        <button class="btn-secondary" style="flex:1;padding:5px;font-size:11px;justify-content:center;" onclick="selectMachine('${{mid}}'); setTab('Performance'); event.stopPropagation();">
          Performance
        </button>
        <button class="${{m.status === 'ANOMALY' ? 'btn-analysis' : 'btn-secondary'}}" style="flex:1;padding:5px;font-size:11px;justify-content:center;" onclick="openAnalysisModal('${{mid}}'); event.stopPropagation();">
          ${{m.status === 'ANOMALY' ? '⚡ Analyze' : 'Inspect'}}
        </button>
      </div>
    `;
    tile.onclick = () => {{ selectMachine(mid); setTab("Performance"); }};
    grid.appendChild(tile);
  }});
}}

function filterMachines(status) {{
  machineFilter = status;
  setTab("Machines");
}}

function renderAlertsList() {{
  const container = document.getElementById("fullAlertsList");
  container.innerHTML = "";

  let list = DATA_BUNDLE.machine_ids.filter(mid => DATA_BUNDLE.machines[mid].status !== "NORMAL");
  if (alertFilter !== "ALL") {{
    list = list.filter(mid => DATA_BUNDLE.machines[mid].status === alertFilter);
  }}
  list.sort((a, b) => (DATA_BUNDLE.machines[b].status === "ANOMALY" ? 1 : 0) - (DATA_BUNDLE.machines[a].status === "ANOMALY" ? 1 : 0));

  if (list.length === 0) {{
    container.innerHTML = `<div class="muted" style="padding:20px;text-align:center;">No active alerts matching filter.</div>`;
    return;
  }}

  list.forEach(mid => {{
    const m = DATA_BUNDLE.machines[mid];
    const isAnom = m.status === "ANOMALY";
    const stColor = isAnom ? "var(--red)" : "var(--amber)";

    const card = document.createElement("div");
    card.className = "alert-item severity-" + m.status;
    card.style.marginBottom = "10px";
    card.style.padding = "14px 16px";
    card.innerHTML = `
      <div class="alert-row">
        <div style="display:flex;align-items:center;gap:10px;">
          <span style="font-size:16px;font-weight:800;color:${{isAnom ? 'var(--red)' : '#fff'}}">${{m.id}}</span>
          <span class="pill pill-${{m.status}}">${{m.status}}</span>
        </div>
        <span class="alert-time" style="font-size:12px;">Anomaly Score: <strong>${{m.latest_score.toFixed(2)}}</strong></span>
      </div>
      <div class="alert-sub" style="font-size:13px;margin:8px 0;">
        ${{isAnom ? 'Critical anomaly detected! Sensor relationship covariance violated learned GNN distribution.' : 'Performance deviation detected across CPU/Memory sub-clusters.'}}
      </div>
      <div style="display:flex;justify-content:flex-end;gap:10px;margin-top:10px;">
        <button class="btn-secondary" onclick="selectMachine('${{mid}}'); setTab('Performance');">View in Performance</button>
        <button class="btn-analysis" onclick="openAnalysisModal('${{mid}}')">⚡ View Root Cause Analysis</button>
      </div>
    `;
    container.appendChild(card);
  }});
}}

function filterAlerts(status) {{
  alertFilter = status;
  renderAlertsList();
}}

function renderHistoryTable() {{
  const tbody = document.getElementById("historyTbody");
  tbody.innerHTML = "";

  DATA_BUNDLE.machine_ids.forEach(mid => {{
    const m = DATA_BUNDLE.machines[mid];
    const rate = (100 * m.num_true_anomalies / Math.max(m.num_points, 1)).toFixed(1);
    const stColor = m.status === "ANOMALY" ? "var(--red)" : (m.status === "WARNING" ? "var(--amber)" : "var(--green)");

    const tr = document.createElement("tr");
    tr.innerHTML = `
      <td style="font-weight:700;cursor:pointer;" onclick="selectMachine('${{mid}}'); setTab('Performance');">${{mid}}</td>
      <td>${{m.num_points}}</td>
      <td>${{m.num_true_anomalies}}</td>
      <td>${{rate}}%</td>
      <td><span class="dot" style="background:${{stColor}}"></span><span style="color:${{stColor}}">${{m.status}}</span></td>
      <td>
        <button class="${{m.status === 'ANOMALY' ? 'btn-analysis' : 'btn-secondary'}}" style="padding:4px 8px;font-size:11.5px;" onclick="openAnalysisModal('${{mid}}')">
          ${{m.status === 'ANOMALY' ? '⚡ Analyze' : 'Inspect'}}
        </button>
      </td>
    `;
    tbody.appendChild(tr);
  }});
}}

function renderPerformance(mid) {{
  const m = DATA_BUNDLE.machines[mid];
  if (!m) return;

  document.getElementById("perfMachineName").innerText = m.id;
  const pill = document.getElementById("perfPill");
  pill.className = "pill pill-" + m.status;
  const stColor = m.status === "ANOMALY" ? "var(--red)" : (m.status === "WARNING" ? "var(--amber)" : "var(--green)");
  pill.innerHTML = `<span class="dot" style="background:${{stColor}}"></span>${{m.status}}`;

  document.getElementById("perfValCPU").innerText = m.cpu.toFixed(0) + "%";
  document.getElementById("perfValMEM").innerText = m.mem.toFixed(0) + "%";
  document.getElementById("perfValDISK").innerText = m.disk.toFixed(0) + "%";
  document.getElementById("perfValNET").innerText = m.net.toFixed(0) + "%";

  document.getElementById("perfScoreText").innerText = m.latest_score.toFixed(2);
  document.getElementById("perfScoreDot").style.background = stColor;
  const stText = document.getElementById("perfScoreStatus");
  stText.style.color = stColor;
  stText.innerText = m.status;

  document.getElementById("perfGroundTruth").innerText = m.num_true_anomalies;
  document.getElementById("perfTotalPoints").innerText = m.num_points;

  renderTimelineChart("perfBigChart", m.history || [], "#3b82f6", 260);
}}

function renderDisk(mid) {{
  const m = DATA_BUNDLE.machines[mid];
  if (!m) return;
  document.getElementById("diskMachineName").innerText = m.id;
  document.getElementById("diskCurrentVal").innerText = m.disk.toFixed(0) + "%";

  renderTimelineChart("diskBigChart", (m.history || []).map(h => ({{ ...h, score: h.disk / 100 }})), "#a855f7", 220);

  const tbody = document.getElementById("diskRankTbody");
  tbody.innerHTML = "";
  const sorted = [...DATA_BUNDLE.machine_ids].sort((a,b) => DATA_BUNDLE.machines[b].disk - DATA_BUNDLE.machines[a].disk);
  sorted.forEach(id => {{
    const node = DATA_BUNDLE.machines[id];
    const tr = document.createElement("tr");
    tr.innerHTML = `
      <td style="font-weight:700;cursor:pointer;" onclick="selectMachine('${{id}}'); setTab('Disk');">${{id}}</td>
      <td style="width:60%;">
        <div style="background:#1c2740;height:8px;border-radius:4px;overflow:hidden;">
          <div style="background:#a855f7;height:100%;width:${{node.disk}}%;"></div>
        </div>
      </td>
      <td style="color:#a855f7;font-weight:700;">${{node.disk.toFixed(0)}}%</td>
      <td><button class="btn-secondary" style="padding:3px 7px;font-size:11px;" onclick="selectMachine('${{id}}'); setTab('Performance');">Inspect</button></td>
    `;
    tbody.appendChild(tr);
  }});
}}

function renderNetwork(mid) {{
  const m = DATA_BUNDLE.machines[mid];
  if (!m) return;
  document.getElementById("netMachineName").innerText = m.id;
  document.getElementById("netCurrentVal").innerText = m.net.toFixed(0) + "%";

  renderTimelineChart("netBigChart", (m.history || []).map(h => ({{ ...h, score: h.net / 100 }})), "#f5a524", 220);

  const tbody = document.getElementById("netRankTbody");
  tbody.innerHTML = "";
  const sorted = [...DATA_BUNDLE.machine_ids].sort((a,b) => DATA_BUNDLE.machines[b].net - DATA_BUNDLE.machines[a].net);
  sorted.forEach(id => {{
    const node = DATA_BUNDLE.machines[id];
    const tr = document.createElement("tr");
    tr.innerHTML = `
      <td style="font-weight:700;cursor:pointer;" onclick="selectMachine('${{id}}'); setTab('Network');">${{id}}</td>
      <td style="width:60%;">
        <div style="background:#1c2740;height:8px;border-radius:4px;overflow:hidden;">
          <div style="background:#f5a524;height:100%;width:${{node.net}}%;"></div>
        </div>
      </td>
      <td style="color:#f5a524;font-weight:700;">${{node.net.toFixed(0)}}%</td>
      <td><button class="btn-secondary" style="padding:3px 7px;font-size:11px;" onclick="selectMachine('${{id}}'); setTab('Performance');">Inspect</button></td>
    `;
    tbody.appendChild(tr);
  }});
}}

function openAnalysisModal(mid) {{
  const m = DATA_BUNDLE.machines[mid] || DATA_BUNDLE.machines["machine-2-2"];
  if (!m) return;

  document.getElementById("modalMid").innerText = m.id;
  const badge = document.getElementById("modalSeverityBadge");
  badge.className = "pill pill-" + m.status;
  badge.innerText = m.status === "ANOMALY" ? "CRITICAL ANOMALY (SCORE: " + m.latest_score.toFixed(2) + ")" : m.status + " (SCORE: " + m.latest_score.toFixed(2) + ")";

  document.getElementById("modalValCPU").innerText = m.cpu.toFixed(1) + "%";
  document.getElementById("modalValMEM").innerText = m.mem.toFixed(1) + "%";
  document.getElementById("modalValDISK").innerText = m.disk.toFixed(1) + "%";
  document.getElementById("modalValNET").innerText = m.net.toFixed(1) + "%";

  const isAnom = m.status === "ANOMALY";
  document.getElementById("devBoxCPU").className = "dev-box" + (m.cpu > 70 ? " anomaly-box" : "");
  document.getElementById("devBoxMEM").className = "dev-box" + (m.mem > 15 || isAnom ? " anomaly-box" : "");
  document.getElementById("devBoxDISK").className = "dev-box" + (m.disk > 70 ? " anomaly-box" : "");
  document.getElementById("devBoxNET").className = "dev-box" + (m.net > 70 ? " anomaly-box" : "");

  document.getElementById("modalDevCPU").innerText = m.cpu > 70 ? "Spike: +42% vs Normal" : "Baseline: Normal";
  document.getElementById("modalDevMEM").innerText = (m.mem > 15 || isAnom) ? "Severe Divergence: +78%" : "Baseline: Normal";
  document.getElementById("modalDevDISK").innerText = m.disk > 70 ? "I/O Throttle: +35%" : "Baseline: Normal";
  document.getElementById("modalDevNET").innerText = m.net > 70 ? "Packet Surge: +55%" : "Baseline: Normal";

  const explBox = document.getElementById("modalGnnExpl");
  if (isAnom) {{
    explBox.innerHTML = `
      <strong>Critical GNN Graph Breakdown Detected on ${{m.id}}:</strong>
      The learned GDNLite Graph Attention Network identifies severe cross-sensor correlation disruption.
      Normal inter-sensor relationships between memory allocation vectors and disk I/O channels experienced a sudden covariance collapse.
      Graph deviation score reached <strong>${{m.latest_score.toFixed(2)}}</strong> (Exceeding the cluster critical threshold of 0.65).
      Statistical deviation index: <strong>+4.82σ</strong> from baseline model weights.
    `;
  }} else {{
    explBox.innerHTML = `
      <strong>Telemetry Topology Report for ${{m.id}}:</strong>
      The Graph Deviation Network indicates that sensor correlation matrices are currently conforming to expected multivariate time-series baselines.
      Anomaly score is <strong>${{m.latest_score.toFixed(2)}}</strong> with no structural topology deviations detected.
    `;
  }}

  renderTimelineChart("modalTimelineChart", m.history || [], isAnom ? "#ef4444" : "#3b82f6", 180);
  document.getElementById("analysisModal").classList.add("open");
}}

function closeAnalysisModal() {{
  document.getElementById("analysisModal").classList.remove("open");
}}

function handleModalOverlayClick(e) {{
  if (e.target.id === "analysisModal") {{
    closeAnalysisModal();
  }}
}}

function renderSparkline(containerId, values, color) {{
  const el = document.getElementById(containerId);
  if (!el) return;
  if (!values || values.length < 2) values = [10, 15, 12, 20, 18];

  const w = 240, h = 50;
  const min = Math.min(...values);
  const max = Math.max(...values);
  const rng = (max - min) || 1;

  const pts = values.map((v, i) => {{
    const x = i * (w / (values.length - 1));
    const y = h - 6 - ((v - min) / rng) * (h - 14);
    return x.toFixed(1) + "," + y.toFixed(1);
  }}).join(" ");

  const area = pts + ` ${{w}},${{h}} 0,${{h}}`;
  const gid = "grad_" + color.replace("#", "");

  el.innerHTML = `
    <svg viewBox="0 0 ${{w}} ${{h}}" width="100%" height="100%" preserveAspectRatio="none">
      <defs>
        <linearGradient id="${{gid}}" x1="0" y1="0" x2="0" y2="1">
          <stop offset="0%" stop-color="${{color}}" stop-opacity="0.35"/>
          <stop offset="100%" stop-color="${{color}}" stop-opacity="0"/>
        </linearGradient>
      </defs>
      <polygon points="${{area}}" fill="url(#${{gid}})"/>
      <polyline points="${{pts}}" fill="none" stroke="${{color}}" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"/>
    </svg>
  `;
}}

function renderLiveMonitoringChart(containerId, hist) {{
  const el = document.getElementById(containerId);
  if (!el) return;
  if (!hist || hist.length === 0) return;

  const w = 780, h = 180;
  const padL = 6, padR = 10, padT = 10, padB = 22;
  const pw = w - padL - padR;
  const ph = h - padT - padB;

  const pts = [];
  const dots = [];
  const n = hist.length;

  hist.forEach((pt, i) => {{
    const x = padL + i * (pw / Math.max(n - 1, 1));
    const val = Math.max(0, Math.min(100, pt.score * 100));
    const y = padT + ph - (val / 100) * ph;
    pts.push(x.toFixed(1) + "," + y.toFixed(1));

    const isAnom = pt.status === "ANOMALY";
    const dotColor = isAnom ? "var(--red)" : "var(--green)";
    const r = isAnom ? 5.5 : 3;
    dots.push(`
      <circle cx="${{x.toFixed(1)}}" cy="${{y.toFixed(1)}}" r="${{r}}" fill="${{dotColor}}">
        <title>t=${{pt.t}} | Score: ${{pt.score.toFixed(2)}} | ${{pt.status}}</title>
      </circle>
    `);
  }});

  const grid = `
    <line x1="${{padL}}" y1="${{padT}}" x2="${{w-padR}}" y2="${{padT}}" stroke="#1c2740" stroke-width="1" stroke-dasharray="3,4"/>
    <line x1="${{padL}}" y1="${{padT + ph/2}}" x2="${{w-padR}}" y2="${{padT + ph/2}}" stroke="#1c2740" stroke-width="1" stroke-dasharray="3,4"/>
    <line x1="${{padL}}" y1="${{padT + ph}}" x2="${{w-padR}}" y2="${{padT + ph}}" stroke="#1c2740" stroke-width="1"/>
  `;

  el.innerHTML = `
    <svg viewBox="0 0 ${{w}} ${{h}}" width="100%" height="100%" preserveAspectRatio="none">
      ${{grid}}
      <polyline points="${{pts.join(" ")}}" fill="none" stroke="var(--green)" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"/>
      ${{dots.join("")}}
    </svg>
  `;
}}

function renderTimelineChart(containerId, hist, strokeColor, height) {{
  const el = document.getElementById(containerId);
  if (!el) return;
  if (!hist || hist.length === 0) return;

  const w = 820, h = height;
  const padL = 10, padR = 10, padT = 15, padB = 20;
  const pw = w - padL - padR;
  const ph = h - padT - padB;

  const pts = [];
  const anomMarkers = [];
  const n = hist.length;

  hist.forEach((pt, i) => {{
    const x = padL + i * (pw / Math.max(n - 1, 1));
    const val = Math.max(0, Math.min(100, (pt.score !== undefined ? pt.score : 0.2) * 100));
    const y = padT + ph - (val / 100) * ph;
    pts.push(x.toFixed(1) + "," + y.toFixed(1));

    if (pt.status === "ANOMALY") {{
      anomMarkers.push(`
        <circle cx="${{x.toFixed(1)}}" cy="${{y.toFixed(1)}}" r="6" fill="var(--red)"/>
        <line x1="${{x.toFixed(1)}}" y1="${{padT}}" x2="${{x.toFixed(1)}}" y2="${{padT + ph}}" stroke="rgba(239,68,68,0.3)" stroke-width="1.5" stroke-dasharray="2,2"/>
      `);
    }}
  }});

  const poly = pts.join(" ");
  const area = poly + ` ${{pts[pts.length-1].split(",")[0]}},${{padT+ph}} ${{padL}},${{padT+ph}}`;
  const gid = "tgrad_" + Math.random().toString(36).substring(7);

  el.innerHTML = `
    <svg viewBox="0 0 ${{w}} ${{h}}" width="100%" height="100%" preserveAspectRatio="none">
      <defs>
        <linearGradient id="${{gid}}" x1="0" y1="0" x2="0" y2="1">
          <stop offset="0%" stop-color="${{strokeColor}}" stop-opacity="0.3"/>
          <stop offset="100%" stop-color="${{strokeColor}}" stop-opacity="0.0"/>
        </linearGradient>
      </defs>
      <polygon points="${{area}}" fill="url(#${{gid}})"/>
      <polyline points="${{poly}}" fill="none" stroke="${{strokeColor}}" stroke-width="2.5" stroke-linecap="round"/>
      ${{anomMarkers.join("")}}
    </svg>
  `;
}}

function renderDonut(containerId, score, color) {{
  const el = document.getElementById(containerId);
  if (!el) return;

  const size = 130, stroke = 11;
  const r = (size - stroke) / 2;
  const c = 2 * Math.PI * r;
  const pct = Math.max(0, Math.min(1, score));
  const dash = c * pct;
  const cx = size / 2, cy = size / 2;

  el.innerHTML = `
    <svg width="${{size}}" height="${{size}}" viewBox="0 0 ${{size}} ${{size}}">
      <circle cx="${{cx}}" cy="${{cy}}" r="${{r}}" fill="none" stroke="#1c2740" stroke-width="${{stroke}}"/>
      <circle cx="${{cx}}" cy="${{cy}}" r="${{r}}" fill="none" stroke="${{color}}" stroke-width="${{stroke}}"
              stroke-linecap="round" stroke-dasharray="${{dash.toFixed(1)}} ${{c.toFixed(1)}}"
              transform="rotate(-90 ${{cx}} ${{cy}})"/>
    </svg>
  `;
}}

function initClock() {{
  function tick() {{
    const now = new Date();
    const opts = {{ month: 'short', day: '2-digit', year: 'numeric', hour: '2-digit', minute: '2-digit', second: '2-digit', hour12: false }};
    document.getElementById("liveClock").innerText = now.toLocaleString('en-US', opts);
  }}
  tick();
  setInterval(tick, 1000);
}}

function startSimulation() {{
  if (simInterval) clearInterval(simInterval);
  simInterval = setInterval(() => {{
    if (!SIMULATION_RUNNING) return;

    const m = DATA_BUNDLE.machines[CURRENT_MACHINE];
    if (m && m.history && m.history.length > 2) {{
      const first = m.history.shift();
      const last = m.history[m.history.length - 1];
      const noise = (Math.random() - 0.5) * 2;
      const nextPt = {{
        t: last.t + 1,
        score: Math.max(0, Math.min(1, last.score + (Math.random() - 0.5) * 0.04)),
        status: last.status,
        cpu: Math.max(5, Math.min(95, last.cpu + noise)),
        mem: Math.max(5, Math.min(95, last.mem + (Math.random() - 0.5))),
        disk: last.disk,
        net: Math.max(5, Math.min(95, last.net + noise * 1.5))
      }};
      m.history.push(nextPt);
      m.cpu = nextPt.cpu;
      m.mem = nextPt.mem;
      m.net = nextPt.net;

      if (CURRENT_TAB === "Overview") {{
        renderLiveMonitoringChart("liveChartContainer", m.history);
        document.getElementById("cardValCPU").innerText = m.cpu.toFixed(0) + "%";
        document.getElementById("cardValMEM").innerText = m.mem.toFixed(0) + "%";
        document.getElementById("cardValNET").innerText = m.net.toFixed(0) + "%";
      }}
    }}
  }}, 2000);
}}

function toggleSimulation() {{
  SIMULATION_RUNNING = !SIMULATION_RUNNING;
  const btn = document.getElementById("simToggleBtn");
  const st = document.getElementById("simStatus");
  if (SIMULATION_RUNNING) {{
    btn.innerText = "⏸ Pause";
    st.innerText = "Live";
    st.style.color = "var(--green)";
  }} else {{
    btn.innerText = "▶ Resume";
    st.innerText = "Paused";
    st.style.color = "var(--amber)";
  }}
}}
</script>

</body>
</html>
"""
