import streamlit as st
import time
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from simulation.assembly_line import AssemblyLine
from dashboard import line_mirror, flow_brain_view, defect_radar_view, stakeholder_views

# --- Page Configuration ---
st.set_page_config(
    page_title="DigitalTwin.ai | Accenture Assembly Intelligence",
    layout="wide",
    initial_sidebar_state="expanded",
)

# --- High-End Accenture Executive Theme CSS ---
st.markdown("""
<style>
    .stApp {
        background-color: #08080C;
        color: #E2E8F0;
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
    }
    
    .accenture-bar {
        height: 3px;
        background: linear-gradient(90deg, #A100FF 0%, #7500C0 40%, #00E5FF 100%);
        border-radius: 2px;
        margin: 10px 0 16px 0;
    }
    
    /* Scenario Banner */
    .scenario-banner {
        background: linear-gradient(135deg, #1C1035 0%, #100C1F 100%);
        border: 1px solid #7500C0;
        border-left: 6px solid #A100FF;
        border-radius: 6px;
        padding: 12px 18px;
        margin-bottom: 16px;
        display: flex;
        justify-content: space-between;
        align-items: center;
    }
    .scenario-title {
        font-size: 13px;
        font-weight: 800;
        color: #FFFFFF;
        letter-spacing: 0.5px;
    }
    .scenario-tag {
        background: #A100FF;
        color: #FFFFFF;
        font-size: 11px;
        font-weight: 700;
        padding: 3px 8px;
        border-radius: 4px;
        text-transform: uppercase;
    }
    
    /* Executive Judge Guide Card */
    .judge-card {
        background: #12121B;
        border: 1px solid #28283C;
        border-left: 4px solid #A100FF;
        border-radius: 6px;
        padding: 14px 18px;
        margin-bottom: 18px;
    }
    .judge-title {
        color: #FFFFFF;
        font-size: 13px;
        font-weight: 800;
        letter-spacing: 0.5px;
        text-transform: uppercase;
        margin-bottom: 6px;
    }
    .judge-body {
        color: #CBD5E1;
        font-size: 12px;
        line-height: 1.5;
    }
    .judge-pill {
        display: inline-block;
        background: rgba(161, 0, 255, 0.25);
        color: #D8B4FE;
        border: 1px solid #7500C0;
        border-radius: 3px;
        padding: 1px 6px;
        font-size: 10px;
        font-weight: 700;
        margin-right: 4px;
    }
    
    /* Metric Cards - Strict High Contrast */
    [data-testid="stMetric"] {
        background: #12121B !important;
        border: 1px solid #28283C !important;
        border-left: 4px solid #A100FF !important;
        border-radius: 6px !important;
        padding: 10px 14px !important;
    }
    [data-testid="stMetricLabel"] p {
        color: #94A3B8 !important;
        font-size: 11px !important;
        font-weight: 700 !important;
        text-transform: uppercase !important;
        letter-spacing: 0.6px !important;
    }
    [data-testid="stMetricValue"] div {
        color: #FFFFFF !important;
        font-size: 22px !important;
        font-weight: 800 !important;
    }
    
    /* Sidebar */
    [data-testid="stSidebar"] {
        background-color: #0D0D14 !important;
        border-right: 1px solid #1E1E2E !important;
    }
    
    /* Buttons */
    .stButton > button {
        background-color: #161622 !important;
        color: #FFFFFF !important;
        border: 1px solid #383850 !important;
        border-radius: 4px !important;
        font-weight: 600 !important;
        font-size: 12px !important;
        transition: all 0.15s ease;
    }
    .stButton > button:hover {
        background-color: #A100FF !important;
        border-color: #A100FF !important;
        color: #FFFFFF !important;
        box-shadow: 0 0 12px rgba(161, 0, 255, 0.4);
    }
    
    /* Tabs */
    .stTabs [data-baseweb="tab-list"] {
        background-color: #12121B;
        border-radius: 6px;
        padding: 3px;
        gap: 4px;
        border: 1px solid #28283C;
    }
    .stTabs [data-baseweb="tab"] {
        color: #94A3B8 !important;
        font-weight: 600 !important;
        border-radius: 4px;
        padding: 6px 14px !important;
        font-size: 13px !important;
    }
    .stTabs [aria-selected="true"] {
        background-color: #7500C0 !important;
        color: #FFFFFF !important;
    }
</style>
""", unsafe_allow_html=True)

# --- Session State ---
if 'sim' not in st.session_state:
    st.session_state.fleet_mode = "Single-Model (Sedans Only)"
    st.session_state.active_anomaly = "None (Normal Operation)"
    st.session_state.sim = AssemblyLine(
        fleet_mode=st.session_state.fleet_mode,
        anomaly=st.session_state.active_anomaly
    )
    st.session_state.is_running = False
    st.session_state.speed = 0.5

sim = st.session_state.sim

# --- Sidebar ---
with st.sidebar:
    st.markdown(
        '<div style="font-size:10px; font-weight:800; color:#A100FF; letter-spacing:1.5px;">ACCENTURE INNOVATION CHALLENGE</div>'
        '<div style="font-size:20px; font-weight:800; color:#FFFFFF; margin-top:2px;">DigitalTwin.ai</div>'
        '<div style="font-size:11px; color:#94A3B8;">Assembly Intelligence Layer (AIL)</div>',
        unsafe_allow_html=True
    )
    st.markdown('<div class="accenture-bar"></div>', unsafe_allow_html=True)

    page = st.radio(
        "Navigation",
        ["Line Mirror", "Flow Brain", "Defect Radar", "Stakeholder Views"],
        index=0,
    )

    st.markdown("---")
    st.markdown("**1. Production Fleet Mode**")
    fleet_options = [
        "Single-Model (Sedans Only)",
        "Mixed-Model (Sedan / SUV / Truck)",
    ]
    selected_fleet = st.radio(
        "Select Vehicle Production Mix:",
        fleet_options,
        index=fleet_options.index(st.session_state.fleet_mode),
        help="Single-model creates a uniform 100% green line. Mixed-model introduces realistic multi-vehicle assembly variations."
    )
    if selected_fleet != st.session_state.fleet_mode:
        st.session_state.fleet_mode = selected_fleet
        st.session_state.sim = AssemblyLine(
            fleet_mode=st.session_state.fleet_mode,
            anomaly=st.session_state.active_anomaly
        )
        st.session_state.is_running = False
        st.rerun()

    st.markdown("---")
    st.markdown("**2. Live Anomaly Injector**")
    st.caption("Trigger or clear factory failure scenarios in real time:")

    anomaly_options = [
        "None (Normal Operation)",
        "Station 4 Bottleneck (Tool Wear Drift)",
        "Sensorless Station 7 (Bayesian Inference)",
        "Quality Gate Interception (1:10:100 Rule)",
    ]
    selected_anomaly = st.selectbox(
        "Inject Anomaly Preset:",
        anomaly_options,
        index=anomaly_options.index(st.session_state.active_anomaly),
        help="Select an anomaly scenario to simulate. Note: Pausing (⏸) freezes the state so you can inspect charts and telemetry in detail."
    )
    if selected_anomaly != st.session_state.active_anomaly:
        st.session_state.active_anomaly = selected_anomaly
        st.session_state.sim.apply_anomaly(selected_anomaly)
        st.rerun()

    st.caption("Note for Evaluators: After selecting an anomaly preset, click Pause (⏸) to freeze the line and view the active anomaly telemetry and alerts.")

    st.markdown("---")
    st.markdown("**3. Live Playback Controls**")
    c1, c2, c3 = st.columns(3)
    with c1:
        btn_txt = "⏸ Pause" if st.session_state.is_running else "▶ Play"
        if st.button(btn_txt, use_container_width=True):
            st.session_state.is_running = not st.session_state.is_running
            st.rerun()
    with c2:
        if st.button("Step +1", use_container_width=True):
            st.session_state.sim.step()
            st.rerun()
    with c3:
        if st.button("Reset", use_container_width=True):
            st.session_state.sim = AssemblyLine(
                fleet_mode=st.session_state.fleet_mode,
                anomaly=st.session_state.active_anomaly
            )
            st.session_state.is_running = False
            st.rerun()

    speed = st.slider("Playback Speed (Seconds / Tick)", 0.1, 2.0, st.session_state.speed, 0.1)
    st.session_state.speed = speed

    st.markdown("---")
    st.caption("Accenture Challenge Round 2 Prototype | Team [PLACEHOLDER]")

# --- Continuous Execution Loop ---
if st.session_state.is_running:
    sim.step()
    time.sleep(st.session_state.speed)
    st.rerun()

# --- Top Header ---
st.markdown('<div class="accenture-bar"></div>', unsafe_allow_html=True)

# Status Indicator Banner
badge_color = "#00C853" if st.session_state.active_anomaly == "None (Normal Operation)" else "#FF3D00"
badge_text = "NORMAL FLOW" if st.session_state.active_anomaly == "None (Normal Operation)" else "ANOMALY INJECTED"

st.markdown(
    f'<div class="scenario-banner">'
    f'<div>'
    f'<div style="color:#94A3B8; font-size:10px; font-weight:700; text-transform:uppercase;">ACTIVE FACTORY CONFIGURATION</div>'
    f'<div class="scenario-title">{st.session_state.fleet_mode} &bull; <span style="color:#FFFFFF;">{st.session_state.active_anomaly}</span></div>'
    f'</div>'
    f'<div class="scenario-tag" style="background-color:rgba(161,0,255,0.2); border-color:{badge_color}; color:#FFFFFF;">{badge_text}</div>'
    f'</div>',
    unsafe_allow_html=True
)

# Route View
if page == "Line Mirror":
    line_mirror.render(sim)
elif page == "Flow Brain":
    flow_brain_view.render(sim)
elif page == "Defect Radar":
    defect_radar_view.render(sim)
elif page == "Stakeholder Views":
    stakeholder_views.render(sim)
