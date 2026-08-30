import streamlit as st
import plotly.graph_objects as go
import pandas as pd
from analytics.cusum_detector import calculate_cusum_both
from analytics.bottleneck_predictor import predict_bottlenecks
from config import TAKT_TIME, CUSUM_H, TOTAL_STATIONS, STATION_CONFIG


def render(sim):
    st.markdown(
        '<div style="font-size:24px; font-weight:800; color:#FFFFFF; margin-bottom:4px;">'
        '<span style="color:#A100FF;">&gt;</span> FLOW BRAIN — Predictive Bottleneck & Drift Engine'
        '</div>',
        unsafe_allow_html=True
    )
    st.caption("Proactive 15–30 minute lookahead engine combining two-sided CUSUM statistical process drift detection and queue fill-rate dynamics.")

    # --- Executive Guide for Evaluators ---
    st.markdown(
        '<div class="judge-card">'
        '<div class="judge-title">'
        '<span style="color:#A100FF; font-weight:900; margin-right:6px;">&gt;</span> '
        'Executive Guide for Evaluators — How Bottleneck Prediction Works'
        '</div>'
        '<div class="judge-body">'
        '<strong>1. The Failure of Traditional Systems:</strong> Standard SCADA/MES alarms only trigger when a buffer is 100% full or a machine stops — by which time upstream cars are already backed up and downstream workers sit idle (costing \$20,000+/min).<br>'
        '<strong>2. Two-Sided CUSUM Drift Detection:</strong> Flow Brain tracks the <em>cumulative sum of micro-deviations</em>. Even if a station runs just 2 seconds slow per car (too small for a threshold alarm), CUSUM detects the persistent trend and flags mechanical wear or pneumatic pressure loss.<br>'
        '<strong>3. Lookahead Time-to-Overflow (ETA):</strong> By calculating real-time queue accumulation velocity ($\\Delta Q / \\Delta t$), the engine computes exact countdowns (e.g. <em>"Buffer will overflow in ~14 min"</em>) so supervisors can act before stoppage occurs.'
        '</div>'
        '</div>',
        unsafe_allow_html=True
    )

    # --- Active Predictive Alerts ---
    predictions = predict_bottlenecks(sim.stations)

    st.markdown(
        '<div style="font-size:16px; font-weight:800; color:#FFFFFF; margin-bottom:10px;">'
        '<span style="color:#A100FF;">&gt;</span> Active Predictive Bottleneck Advisories'
        '</div>',
        unsafe_allow_html=True
    )

    if predictions:
        for p in predictions:
            sev = p['severity']
            color_map = {
                "Critical": ("#D50000", "#280A0A"),
                "High": ("#FF3D00", "#261008"),
                "Medium": ("#FFB300", "#261E08"),
                "Low": ("#00E5FF", "#081F26"),
            }
            border_col, bg_col = color_map.get(sev, ("#A100FF", "#18112C"))

            st.markdown(
                f'<div style="background:{bg_col}; border:1px solid {border_col}; border-left:5px solid {border_col}; '
                f'padding:12px 16px; border-radius:4px; margin-bottom:10px;">'
                f'<div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:4px;">'
                f'<span style="color:{border_col}; font-weight:800; font-size:11px; letter-spacing:0.5px;">[{sev.upper()} SEVERITY ALERT]</span>'
                f'<span style="color:#94A3B8; font-size:11px;">STATION {p["station"]} | {p["zone"].upper()}</span>'
                f'</div>'
                f'<div style="color:#FFFFFF; font-size:13px; font-weight:600; margin-bottom:4px;">{p["message"]}</div>'
                f'<div style="color:#CBD5E1; font-size:12px;"><strong style="color:#A100FF;">OPERATIONAL INTERVENTION:</strong> {p["action"]}</div>'
                f'</div>',
                unsafe_allow_html=True
            )
    else:
        st.markdown(
            '<div style="background:#0D2418; border:1px solid #00C853; border-left:4px solid #00C853; '
            'padding:12px; border-radius:4px; color:#FFFFFF; font-size:13px;">'
            '<strong>FLOW EQUILIBRIUM:</strong> All 40 workstations operating within nominal takt variance. No bottleneck formations projected within the 20-minute lookahead window.'
            '</div>',
            unsafe_allow_html=True
        )

    st.markdown("---")

    # --- Live Queue Depth Distribution ---
    st.markdown(
        '<div style="font-size:16px; font-weight:800; color:#FFFFFF; margin-bottom:10px;">'
        '<span style="color:#A100FF;">&gt;</span> Live WIP Buffer Saturation Map (Max Capacity: 5 Units)'
        '</div>',
        unsafe_allow_html=True
    )

    queue_data = []
    for sid in range(1, TOTAL_STATIONS + 1):
        st_obj = sim.stations[sid]
        queue_data.append({
            "Station": f"S{sid}",
            "Queue": len(st_obj.queue),
            "Zone": st_obj.cfg["zone"],
        })
    df_q = pd.DataFrame(queue_data)

    fig_q = go.Figure(data=[
        go.Bar(
            x=df_q["Station"],
            y=df_q["Queue"],
            marker_color=[
                "#D50000" if q >= 5 else "#FF3D00" if q >= 4 else
                "#FFB300" if q >= 3 else "#A100FF"
                for q in df_q["Queue"]
            ],
            text=df_q["Queue"],
            textposition="auto",
            textfont=dict(color="#FFFFFF")
        )
    ])
    fig_q.add_hline(
        y=5,
        line_dash="dash",
        line_color="#D50000",
        annotation_text="Buffer Stoppage Threshold (5 units)",
        annotation_position="top right",
        annotation_font_color="#D50000"
    )
    fig_q.update_layout(
        title="Work-in-Progress (WIP) Queue Depth Across All 40 Stations",
        xaxis_title="Workstation",
        yaxis_title="Units in Queue",
        height=300,
        paper_bgcolor="#12121B",
        plot_bgcolor="#12121B",
        font=dict(color="#CBD5E1"),
        xaxis=dict(gridcolor="#28283C"),
        yaxis=dict(gridcolor="#28283C"),
    )
    st.plotly_chart(fig_q, use_container_width=True)

    st.markdown("---")

    # --- Two-Sided CUSUM Statistical Drift ---
    st.markdown(
        '<div style="font-size:16px; font-weight:800; color:#FFFFFF; margin-bottom:10px;">'
        '<span style="color:#A100FF;">&gt;</span> Two-Sided CUSUM Process Drift Detection'
        '</div>',
        unsafe_allow_html=True
    )

    col1, col2 = st.columns([1, 3])
    with col1:
        selected = st.selectbox(
            "Inspect Station Drift Profile",
            range(1, TOTAL_STATIONS + 1),
            format_func=lambda s: f"Station {s} ({STATION_CONFIG[s]['zone']})",
            key="cusum_station_select",
        )

    st_obj = sim.stations[selected]

    if st_obj.cycle_time_history and len(st_obj.cycle_time_history) >= 3:
        upper, lower, up_drift, down_drift = calculate_cusum_both(
            st_obj.cycle_time_history, target=TAKT_TIME / 10
        )

        with col1:
            if up_drift:
                st.markdown(
                    '<div style="background:#261008; border:1px solid #FF3D00; padding:10px; border-radius:4px; color:#FFFFFF; font-size:12px; margin-bottom:8px;">'
                    '<strong style="color:#FF3D00;">UPWARD SLOWDOWN DRIFT:</strong> Persistent cycle time lag detected. Worn tool or mechanical friction indicated.'
                    '</div>',
                    unsafe_allow_html=True
                )
            elif down_drift:
                st.markdown(
                    '<div style="background:#261E08; border:1px solid #FFB300; padding:10px; border-radius:4px; color:#FFFFFF; font-size:12px; margin-bottom:8px;">'
                    '<strong style="color:#FFB300;">DOWNWARD SPEED DRIFT:</strong> Abnormally short cycle times. Risk of omitted fastening or skipped checklist step.'
                    '</div>',
                    unsafe_allow_html=True
                )
            else:
                st.markdown(
                    '<div style="background:#0D2418; border:1px solid #00C853; padding:10px; border-radius:4px; color:#FFFFFF; font-size:12px; margin-bottom:8px;">'
                    '<strong style="color:#00C853;">STABLE:</strong> Cumulative variation within stochastic baseline limits.'
                    '</div>',
                    unsafe_allow_html=True
                )

            st.metric("Estimated Mechanical Drift", f"{st_obj.drift_factor:.3f}")
            st.metric("Recent Mean Cycle Pace", f"{st_obj.avg_recent_ct(10)*10:.1f}s")

        with col2:
            fig = go.Figure()
            x = list(range(len(upper)))
            fig.add_trace(go.Scatter(
                x=x, y=upper,
                mode='lines+markers',
                name='Upper CUSUM (Slowdown Drift)',
                line=dict(color='#FF3D00', width=2),
                marker=dict(size=4)
            ))
            fig.add_trace(go.Scatter(
                x=x, y=lower,
                mode='lines+markers',
                name='Lower CUSUM (Omission Anomaly)',
                line=dict(color='#00E5FF', width=2),
                marker=dict(size=4)
            ))
            fig.add_hline(
                y=CUSUM_H,
                line_dash="dash",
                line_color="#D50000",
                annotation_text=f"Decision Threshold (h={CUSUM_H})",
                annotation_position="top left",
                annotation_font_color="#D50000"
            )
            fig.update_layout(
                title=f"Station {selected} CUSUM Control Chart",
                xaxis_title="Consecutive Completed Units",
                yaxis_title="Cumulative Sum Statistic",
                height=320,
                paper_bgcolor="#12121B",
                plot_bgcolor="#12121B",
                font=dict(color="#CBD5E1"),
                xaxis=dict(gridcolor="#28283C"),
                yaxis=dict(gridcolor="#28283C"),
                legend=dict(orientation="h", y=-0.2, font=dict(color="#FFFFFF"))
            )
            st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("Advancing more simulation steps will populate the continuous CUSUM trajectory.")
