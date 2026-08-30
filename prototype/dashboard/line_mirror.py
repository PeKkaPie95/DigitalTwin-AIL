import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from config import TOTAL_STATIONS, TAKT_TIME, STATION_CONFIG, ZONES, QUALITY_GATES, STATUS_COLORS
from analytics.cusum_detector import neighbor_inference


def render(sim):
    st.markdown(
        '<div style="font-size:22px; font-weight:800; color:#FFFFFF; margin-bottom:4px;">'
        '<span style="color:#A100FF;">&gt;</span> LINE MIRROR — Real-Time Production Rhythm'
        '</div>',
        unsafe_allow_html=True
    )
    st.caption("Live operational model tracking cycle pace, work-in-progress (WIP) buffer queues, and Bayesian neighbor inference across 40 workstations.")

    # --- Executive Guide for Evaluators ---
    st.markdown(
        '<div class="judge-card">'
        '<div class="judge-title">'
        '<span style="color:#A100FF; font-weight:900; margin-right:6px;">&gt;</span> '
        'Executive Guide for Evaluators — What You Are Observing'
        '</div>'
        '<div class="judge-body">'
        '<strong>1. The Principle:</strong> We deliberately model the <em>rhythm</em> (cycle time vs. takt, queue depths) rather than heavy 3D CAD geometry. 3D twins look impressive but provide zero predictive value.<br>'
        '<strong>2. Sensorless Stations:</strong> Real plants have legacy stations without digital sensors. Observe stations marked <span class="judge-pill">[INFERRED]</span> (e.g. S7, S11). Our <em>Neighbor Inference Engine</em> mathematically estimates their cycle state using flanking station rates and propagates Bayesian uncertainty bands ($P(\\text{Normal})$ vs. $P(\\text{Slow})$).<br>'
        '<strong>3. Immediate Status:</strong> Color bars show real-time line health (<span style="color:#00C853; font-weight:700;">Green</span> = Nominal, <span style="color:#FFB300; font-weight:700;">Yellow</span> = Cycle Drift, <span style="color:#FF3D00; font-weight:700;">Red</span> = Critical Bottleneck).'
        '</div>'
        '</div>',
        unsafe_allow_html=True
    )

    # --- KPI Summary Row ---
    k1, k2, k3, k4 = st.columns(4)
    active = sim.get_active_vehicles()
    k1.metric("WIP Units on Line", f"{len(active)} units")
    k2.metric("Completed Units", f"{len(sim.completed_vehicles)} units")
    k3.metric("Quality Gate Interceptions", f"{len(sim.flagged_vehicles)} units")
    k4.metric("Active Simulation Time", f"t = {sim.time}")

    st.markdown("---")

    # --- 40-Station Assembly Grid by Zone ---
    for zone_name, zone_info in ZONES.items():
        start, end = zone_info["range"]
        st.markdown(
            f'<div style="font-size:13px; font-weight:800; color:#FFFFFF; margin-bottom:8px; border-left:3px solid {zone_info["color"]}; padding-left:8px; letter-spacing:0.5px;">'
            f'{zone_name.upper()} (STATIONS {start} TO {end})'
            f'</div>',
            unsafe_allow_html=True
        )

        cols = st.columns(min(end - start + 1, 10))
        for idx, sid in enumerate(range(start, end + 1)):
            st_obj = sim.stations[sid]
            col_idx = idx % len(cols)

            status_border = {
                "Normal": "#00C853",
                "Idle": "#4B5563",
                "Warning": "#FFB300",
                "Critical": "#FF3D00",
                "Blocked": "#D50000"
            }.get(st_obj.status, "#4B5563")

            status_bg = {
                "Normal": "#101B15",
                "Idle": "#12121B",
                "Warning": "#261E08",
                "Critical": "#2E0E0E",
                "Blocked": "#300808"
            }.get(st_obj.status, "#12121B")

            cov = STATION_CONFIG[sid]["coverage"]
            cov_label = "FULL" if cov == 2 else ("PARTIAL" if cov == 1 else "INFERRED")
            cov_color = "#A100FF" if cov == 2 else ("#00E5FF" if cov == 1 else "#94A3B8")

            qg_badge = '<div style="font-size:9px; font-weight:800; color:#FFD700; letter-spacing:0.5px;">[Q-GATE]</div>' if sid in QUALITY_GATES else ''
            q_len = len(st_obj.queue)
            ct_display = f"{st_obj.avg_recent_ct(3)*10:.0f}s" if st_obj.cycle_time_history else "60s"

            with cols[col_idx]:
                st.markdown(
                    f'<div style="background-color:{status_bg}; border:1px solid #28283C; border-top:4px solid {status_border}; '
                    f'padding:8px 2px; border-radius:4px; text-align:center; color:#FFFFFF; margin-bottom:8px;">'
                    f'<div style="font-size:13px; font-weight:800;">S{sid}</div>'
                    f'{qg_badge}'
                    f'<div style="font-size:9px; font-weight:700; color:{cov_color}; margin:1px 0;">[{cov_label}]</div>'
                    f'<div style="font-size:10px; color:#E2E8F0; font-weight:600;">Q:{q_len}/5</div>'
                    f'<div style="font-size:10px; color:#94A3B8;">{ct_display}</div>'
                    f'</div>',
                    unsafe_allow_html=True,
                )

    # --- Station Status Legend ---
    st.markdown("**Workstation Status Guide:**")
    l_cols = st.columns(5)
    l_items = [
        ("Nominal Cadence", "#00C853"),
        ("Cycle Creep / Warning", "#FFB300"),
        ("Critical Bottleneck / Jam", "#FF3D00"),
        ("Buffer Fully Saturated", "#D50000"),
        ("Idle / Starved Workstation", "#4B5563"),
    ]
    for col, (label, color) in zip(l_cols, l_items):
        col.markdown(
            f'<div style="display:flex; align-items:center; gap:6px; font-size:11px; color:#CBD5E1;">'
            f'<span style="width:10px; height:10px; border-radius:2px; background:{color}; display:inline-block;"></span> {label}'
            f'</div>',
            unsafe_allow_html=True
        )

    st.markdown("---")

    # --- Station Telemetry Drilldown ---
    st.markdown(
        '<div style="font-size:15px; font-weight:800; color:#FFFFFF; margin-bottom:10px;">'
        '<span style="color:#A100FF;">&gt;</span> Station Telemetry & Inference Deep-Dive'
        '</div>',
        unsafe_allow_html=True
    )

    selected = st.selectbox(
        "Select Workstation to Inspect",
        range(1, TOTAL_STATIONS + 1),
        format_func=lambda s: f"Station {s} — {STATION_CONFIG[s]['zone']}"
    )
    st_obj = sim.stations[selected]
    cfg = STATION_CONFIG[selected]

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Station Health", st_obj.status.upper())
    c2.metric("Buffer Queue", f"{len(st_obj.queue)} / 5 units")
    cov_text = "Full Sensors (Telemetry Active)" if cfg["coverage"] == 2 else ("Partial (Torque/Power)" if cfg["coverage"] == 1 else "Sensorless (Neighbor Inference)")
    c3.metric("Instrumentation Level", cov_text)
    avg_ct = f"{st_obj.avg_recent_ct(5)*10:.1f}s" if st_obj.cycle_time_history else "60.0s"
    c4.metric("Current Mean Cycle", avg_ct)

    # Plotly Cycle Time History
    if st_obj.cycle_time_history:
        display_ct = [ct * 10 for ct in st_obj.cycle_time_history]
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            y=display_ct,
            mode='lines+markers',
            name='Actual Station Cycle Time',
            line=dict(color='#A100FF', width=2),
            marker=dict(size=5, color='#00E5FF'),
        ))
        fig.add_hline(
            y=TAKT_TIME,
            line_dash="dash",
            line_color="#FF3D00",
            annotation_text=f"Target Takt Pace ({TAKT_TIME}s)",
            annotation_position="bottom right",
            annotation_font_color="#FF3D00"
        )
        fig.update_layout(
            title=f"Station {selected} Cycle Time Trajectory vs. Target Takt ({TAKT_TIME}s)",
            xaxis_title="Completed Vehicle Sequence",
            yaxis_title="Cycle Duration (seconds)",
            height=280,
            paper_bgcolor="#12121B",
            plot_bgcolor="#12121B",
            font=dict(color="#CBD5E1"),
            xaxis=dict(gridcolor="#28283C"),
            yaxis=dict(gridcolor="#28283C"),
        )
        st.plotly_chart(fig, use_container_width=True)

    # Bayesian Neighbor Inference Display for Unmonitored Stations
    if cfg["coverage"] == 0:
        st.markdown(
            '<div style="background:#18112C; border:1px solid #7500C0; padding:14px; border-radius:6px; margin-top:14px;">'
            '<div style="color:#A100FF; font-weight:800; font-size:13px; margin-bottom:4px;">NEIGHBOR INFERENCE ENGINE — SENSORLESS WORKSTATION RESOLUTION</div>'
            '<div style="color:#CBD5E1; font-size:12px; margin-bottom:10px;">This workstation has no physical process sensors. Our model estimates internal parameters by measuring input/output flow rates from adjacent flanking stations.</div>',
            unsafe_allow_html=True
        )
        inf = neighbor_inference(sim.stations, selected)
        ic1, ic2, ic3 = st.columns(3)
        ic1.metric("Inferred Cycle Time", f"{inf['inferred_cycle_time']*10:.1f}s")
        ic2.metric("Normal Pace Probability P(N)", f"{inf['probability_normal']:.0%}")
        ic3.metric("95% Credible Interval", f"{inf['confidence_interval'][0]*10:.0f}s - {inf['confidence_interval'][1]*10:.0f}s")
        st.caption(f"Mathematical Formulation: {inf['method']} | Bayesian Prior: Calibrated against shift model mix.")
        st.markdown('</div>', unsafe_allow_html=True)
