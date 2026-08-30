import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from analytics.defect_scorer import (
    get_risk_label, format_risk_breakdown, generate_risk_explanation,
)
from config import RISK_THRESHOLDS, RISK_COLORS


def render(sim):
    st.markdown(
        '<div style="font-size:24px; font-weight:800; color:#FFFFFF; margin-bottom:4px;">'
        '<span style="color:#A100FF;">&gt;</span> DEFECT RADAR — In-Process Quality Intelligence'
        '</div>',
        unsafe_allow_html=True
    )
    st.caption("Per-vehicle rolling risk passports (0–100) tracking micro-deviations to intercept defects at intermediate Quality Gates.")

    # --- Executive Guide for Evaluators ---
    st.markdown(
        '<div class="judge-card">'
        '<div class="judge-title">'
        '<span style="color:#A100FF; font-weight:900; margin-right:6px;">&gt;</span> '
        'Executive Guide for Evaluators — The 1:10:100 Rule & Explainable AI'
        '</div>'
        '<div class="judge-body">'
        '<strong>1. The 1:10:100 Manufacturing Rule:</strong> A defect caught in-process costs <strong>1x</strong> to fix. Caught at end-of-line after full vehicle assembly, it costs <strong>10x</strong> (requiring teardown). Caught by the consumer via warranty/recall, it costs <strong>100x+</strong>.<br>'
        '<strong>2. Explainable AI Quality Passport:</strong> Every car carries an immutable digital ledger. Risk is not a black-box number: Defect Radar maps exact physical root causes (e.g., loose torque at S3, thermal spike in paint curing at S15, or sensorless uncertainty at S7).<br>'
        '<strong>3. Intermediate Quality Gates (S12, S20, S40):</strong> High-risk units are intercepted at zonal boundaries rather than allowing latent flaws to propagate through the entire plant.'
        '</div>'
        '</div>',
        unsafe_allow_html=True
    )

    # --- KPI Row ---
    k1, k2, k3, k4 = st.columns(4)
    active = sim.get_active_vehicles()
    completed = sim.completed_vehicles
    flagged = sim.flagged_vehicles

    k1.metric("Active Units Monitored", len(active))
    k2.metric("Passed Quality Gates", len(completed))
    k3.metric("Intercepted at In-Line Gates", len(flagged))
    defect_rate = sim.get_defect_rate()
    k4.metric("In-Process Defect Rate", f"{defect_rate:.1f}%")

    st.markdown("---")

    # --- Active Vehicle Risk Registry ---
    st.markdown(
        '<div style="font-size:16px; font-weight:800; color:#FFFFFF; margin-bottom:10px;">'
        '<span style="color:#A100FF;">&gt;</span> Live Vehicle Risk Registry (Ranked by Vulnerability)'
        '</div>',
        unsafe_allow_html=True
    )

    if active:
        rows = [{
            "Vehicle ID": v.id,
            "Model Variant": v.model,
            "Current Station": f"Station {v.current_station}",
            "Risk Score": round(v.accumulated_risk, 1),
            "Risk Category": get_risk_label(v.accumulated_risk).upper(),
            "Stations Completed": len(v.process_history),
        } for v in active]

        df = pd.DataFrame(rows).sort_values("Risk Score", ascending=False).reset_index(drop=True)
        st.dataframe(df, use_container_width=True, height=240)

        # Charts
        c1, c2 = st.columns(2)
        with c1:
            fig = px.histogram(
                df,
                x="Risk Score",
                nbins=20,
                color_discrete_sequence=["#A100FF"],
                title="WIP Risk Score Frequency Distribution",
            )
            fig.update_layout(
                height=260,
                paper_bgcolor="#12121B",
                plot_bgcolor="#12121B",
                font=dict(color="#CBD5E1"),
                xaxis=dict(gridcolor="#28283C"),
                yaxis=dict(gridcolor="#28283C"),
            )
            st.plotly_chart(fig, use_container_width=True)

        with c2:
            risk_counts = df["Risk Category"].value_counts()
            fig2 = px.pie(
                values=risk_counts.values,
                names=risk_counts.index,
                color=risk_counts.index,
                color_discrete_map={
                    "NORMAL": RISK_COLORS["normal"],
                    "ELEVATED": RISK_COLORS["elevated"],
                    "HIGH": RISK_COLORS["high"],
                    "CRITICAL": RISK_COLORS["critical"],
                },
                title="Cohort Risk Categorization",
            )
            fig2.update_layout(
                height=260,
                paper_bgcolor="#12121B",
                font=dict(color="#CBD5E1"),
                legend=dict(font=dict(color="#FFFFFF"))
            )
            st.plotly_chart(fig2, use_container_width=True)

        st.markdown("---")

        # --- Explainable AI Drilldown ---
        st.markdown(
            '<div style="font-size:16px; font-weight:800; color:#FFFFFF; margin-bottom:10px;">'
            '<span style="color:#A100FF;">&gt;</span> Explainable AI — Unit Digital Passport Drilldown'
            '</div>',
            unsafe_allow_html=True
        )

        vehicle_options = sorted(active, key=lambda v: -v.accumulated_risk)
        selected_id = st.selectbox(
            "Select Vehicle to Inspect Quality Passport Ledger",
            [v.id for v in vehicle_options],
            format_func=lambda vid: next(
                f"{vid} ({v.model}) — Risk Score: {v.accumulated_risk:.1f}/100 [{get_risk_label(v.accumulated_risk).upper()}]"
                for v in vehicle_options if v.id == vid
            ),
        )
        selected_v = next(v for v in vehicle_options if v.id == selected_id)

        st.markdown(
            '<div style="background:#18112C; border:1px solid #7500C0; border-left:4px solid #A100FF; '
            'padding:14px 18px; border-radius:6px; color:#FFFFFF; margin-bottom:14px;">'
            f'<div style="font-size:14px; font-weight:800; color:#FFFFFF; margin-bottom:6px;">'
            f'DIGITAL QUALITY PASSPORT: {selected_v.id} ({selected_v.model})'
            f'</div>'
            f'<div style="font-size:12px; color:#CBD5E1; line-height:1.6;">'
            f'{generate_risk_explanation(selected_v)}'
            f'</div>'
            '</div>',
            unsafe_allow_html=True
        )

        # Cumulative Risk Trajectory
        if selected_v.process_history:
            cumulative = []
            running = 0
            for rec in selected_v.process_history:
                running += rec["risk_added"]
                cumulative.append({
                    "Station": f"S{rec['station']}",
                    "Cumulative Risk": round(running, 1),
                    "Delta Added": round(rec["risk_added"], 1),
                })
            df_risk = pd.DataFrame(cumulative)

            fig3 = go.Figure()
            fig3.add_trace(go.Scatter(
                x=df_risk["Station"],
                y=df_risk["Cumulative Risk"],
                mode="lines+markers",
                name="Cumulative Defect Risk",
                line=dict(color="#A100FF", width=3),
                marker=dict(size=6, color="#00E5FF"),
                fill="tozeroy",
                fillcolor="rgba(161, 0, 255, 0.15)",
            ))
            fig3.add_trace(go.Bar(
                x=df_risk["Station"],
                y=df_risk["Delta Added"],
                name="Station Risk Inception Delta",
                marker_color="rgba(0, 229, 255, 0.5)",
            ))
            fig3.add_hline(y=30, line_dash="dot", line_color="#FFB300", annotation_text="Elevated Risk Level (30)")
            fig3.add_hline(y=60, line_dash="dot", line_color="#FF3D00", annotation_text="Quality Gate Interception Level (60)")
            fig3.add_hline(y=80, line_dash="dash", line_color="#D50000", annotation_text="Critical Quarantine Level (80)")
            fig3.update_layout(
                title=f"Vehicle {selected_v.id} Station-by-Station Defect Risk Accumulation",
                xaxis_title="Assembly Station",
                yaxis_title="Calculated Risk Metric (0-100)",
                height=300,
                paper_bgcolor="#12121B",
                plot_bgcolor="#12121B",
                font=dict(color="#CBD5E1"),
                xaxis=dict(gridcolor="#28283C"),
                yaxis=dict(gridcolor="#28283C"),
                legend=dict(orientation="h", y=-0.2, font=dict(color="#FFFFFF"))
            )
            st.plotly_chart(fig3, use_container_width=True)

    else:
        st.info("Simulation initialized. Run steps to observe vehicle flow.")

    st.markdown("---")

    # --- Quality Gate Interception Table ---
    st.markdown(
        '<div style="font-size:16px; font-weight:800; color:#FFFFFF; margin-bottom:10px;">'
        '<span style="color:#A100FF;">&gt;</span> Intermediate Quality Gate Interception Log (1:10:100 In Action)'
        '</div>',
        unsafe_allow_html=True
    )

    if flagged:
        flagged_rows = [{
            "Vehicle ID": v.id,
            "Model": v.model,
            "Quarantine Risk": round(v.accumulated_risk, 1),
            "Intercepted At": f"Station {v.flagged_at_gate}",
            "Stations Traversed": len(v.process_history),
            "Primary Anomaly Trigger": v.risk_breakdown[-1][1] if v.risk_breakdown else "Multi-factor accumulation",
        } for v in flagged[-15:]]
        st.dataframe(pd.DataFrame(flagged_rows), use_container_width=True)
    else:
        st.caption("No vehicles have breached the Quality Gate threshold yet.")
