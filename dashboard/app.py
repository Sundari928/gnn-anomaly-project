"""
Streamlit dashboard for the GNN-Based Server Monitoring & Anomaly Detection system.
Renders the complete interactive Single Page Application (SPA).

Run: streamlit run dashboard/app.py
"""
import os
import sys
import streamlit as st
import streamlit.components.v1 as components

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from render import get_dashboard_html

st.set_page_config(
    page_title="Server Monitoring & Anomaly Detection",
    page_icon="🖥️",
    layout="wide",
    initial_sidebar_state="collapsed",
)

st.markdown("""
<style>
  #MainMenu, header, footer { visibility: hidden !important; }
  .block-container { padding: 0 !important; max-width: 100% !important; margin: 0 !important; }
  iframe { border: none !important; }
</style>
""", unsafe_allow_html=True)

html_content = get_dashboard_html()
components.html(html_content, height=1150, scrolling=True)
