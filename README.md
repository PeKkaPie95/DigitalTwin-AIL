# DigitalTwin.ai — AI-Powered Digital Twin for Vehicle Assembly Lines

> **Accenture Innovation Challenge 2026 — Round 2 (Prototype Round)**  
> **Problem Track 4:** DigitalTwin.ai  
> **Team:** [TEAM_NAME_PLACEHOLDER]

[![Python 3.10](https://img.shields.io/badge/python-3.10-purple.svg)](https://www.python.org/downloads/release/python-3100/)
[![Framework](https://img.shields.io/badge/framework-Streamlit%20%7C%20Plotly-blue.svg)](https://streamlit.io/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)

---

## Executive Summary

Modern vehicle manufacturing lines incur **$20,000+ per minute** during unplanned line stoppages. Conventional digital twin implementations rely heavily on complex 3D CAD visualization that, while visually impressive, provides zero forward-looking predictive value. Furthermore, real-world brownfield plants suffer from uneven telemetry coverage where up to 30% of legacy workstations have no digital process instrumentation.

**DigitalTwin.ai** implements the **Assembly Intelligence Layer (AIL)** — a high-performance digital twin architecture that models the **rhythm** of the manufacturing line rather than its physical geometry:
- **Flow Brain:** Projects imminent bottleneck formations **15–30 minutes** in advance using two-sided CUSUM statistical drift detection and dynamic queue fill-rate regressions.
- **Defect Radar:** Tracks an immutable, explainable risk score (0–100) for every individual vehicle unit ($VH\text{-}XXXX$) as it advances through each workstation, intercepting latent defects at intermediate Quality Gates.
- **Line Mirror:** Delivers real-time operational visibility across 40 workstations across Body Construction, Paint, and Final Assembly, with **Bayesian Neighbor Inference** estimating states for unmonitored legacy stations.
- **Role-Based Intelligence:** Tailors intelligence feeds for Floor Supervisors (real-time dispatch), Plant Operations Managers (shift OEE & Pareto analysis), and Executive Leadership (quantified downtime valuation & enterprise scaling).

---

## System Architecture

```
                               ┌─────────────────────────────┐
                               │  Factory Floor Telemetry    │
                               │  PLCs, Smart Tools, Cameras │
                               └──────────────┬──────────────┘
                                              │
                      ┌───────────────────────┼───────────────────────┐
                      ▼                       ▼                       ▼
            ┌───────────────────┐   ┌───────────────────┐   ┌───────────────────┐
            │    LINE MIRROR    │   │    FLOW BRAIN     │   │   DEFECT RADAR    │
            │  40-Station Model │   │ CUSUM Drift &     │   │ Per-Vehicle Risk  │
            │  Cycle vs Takt    │   │ 20-min Bottleneck │   │ Scoring & Quality │
            │  Neighbor Infer.  │   │ Lookahead Engine  │   │ Gate Interception │
            └─────────┬─────────┘   └─────────┬─────────┘   └─────────┬─────────┘
                      │                       │                       │
                      └───────────────────────┼───────────────────────┘
                                              ▼
                               ┌─────────────────────────────┐
                               │   Explainable AI Engine     │
                               │   Plain-English Root Cause  │
                               └──────────────┬──────────────┘
                                              ▼
                ┌─────────────────────────────┼─────────────────────────────┐
                ▼                             ▼                             ▼
     ┌─────────────────────┐       ┌─────────────────────┐       ┌─────────────────────┐
     │  FLOOR SUPERVISOR   │       │    PLANT MANAGER    │       │     LEADERSHIP      │
     │  Real-Time Triage   │       │  Shift OEE & Trends │       │  ROI & Payback (<1m)│
     └─────────────────────┘       └─────────────────────┘       └─────────────────────┘
```

---

## Installation & Local Execution

### Prerequisites
- Python 3.10+
- Anaconda or Miniconda

### 1. Clone & Set Up Environment
```bash
# Clone the repository
git clone https://github.com/PeKkaPie95/DigitalTwin-AIL.git
cd DigitalTwin-AIL/prototype

# Create & activate conda environment
conda create -n digitaltwin python=3.10 -y
conda activate digitaltwin

# Install dependencies
pip install -r requirements.txt
```

### 2. Launch the Application
```bash
streamlit run app.py
```
Access the application dashboard at `http://localhost:8501`.

---

## Prototype Features & Evaluation Guide

1. **Modular Sidebar Controls:**
   - **Production Fleet Mode:** Toggle between **Single-Model Line (Sedans Only — Uniform 60s Takt / Solid Green)** and **Mixed-Model Flexible Line (Sedan / SUV / Truck — Model Mix Variance)**.
   - **Live Anomaly Injector:** Dynamically trigger or clear factory scenarios in real time:
     - `None (Normal Operation)`: Clean, healthy baseline flow.
     - `Station 4 Bottleneck (Tool Wear Drift)`: Simulates mechanical tool degradation, buffer queue backup to 5/5, and upstream blockage.
     - `Sensorless Station 7 (Bayesian Inference)`: Tests Bayesian neighbor inference on an unmonitored legacy workstation.
     - `Quality Gate Interception (1:10:100 Rule)`: Demonstrates automated risk scoring and defect quarantine at Station 12.
   - **Live Playback Controls:** `Play / Pause` toggle, `Step +1` manual advance, `Reset`, and playback speed slider.

2. **Line Mirror Console:**
   - Visualizes all 40 stations across **Body Construction** (S1–S12), **Paint Shop** (S13–S20), and **Final Assembly** (S21–S40).
   - Shows instrumentation status: `[FULL]`, `[PARTIAL]`, or `[INFERRED]`.
   - Evaluates unmonitored legacy stations via **Neighbor Inference** with Bayesian credible intervals ($P(\text{Normal})$ vs $P(\text{Slow})$).

3. **Flow Brain Prediction Console:**
   - Active lookahead advisories displaying real-time countdowns to buffer saturation.
   - Two-sided CUSUM statistical process control charts capturing micro-delays before hard threshold alarms trigger.
   - Live cross-station Work-in-Progress (WIP) buffer queue distribution.

4. **Defect Radar Quality Console:**
   - Live vehicle risk registry ranked by vulnerability score ($0–100$).
   - Unit Digital Quality Passport drilldown providing plain-English root-cause attribution (e.g., torque drift at S4, thermal spike at S15, uncertainty penalty at S7).
   - In-line Quality Gate quarantine logs demonstrating the **1:10:100 Cost Reduction Principle** ($1 in-process vs $10 end-of-line vs $100+ recall).

5. **Stakeholder Intelligence Views:**
   - **Floor Supervisor:** Tactical console for immediate operator dispatch and 20-minute predictive lookaheads.
   - **Plant Operations Manager:** Shift schedule attainment, OEE tracking, and chronic bottleneck Pareto analysis.
   - **Executive Leadership:** Valuation of avoided line downtime ($20,000/min), quality rework savings, and capital payback period ($<1$ month).

---

## 3-Minute Video Demonstration Script

Follow this structured script when recording your 3-minute evaluation video:

| Timestamp | Section & Navigation | Talking Points |
| :--- | :--- | :--- |
| **0:00 – 0:40** | **Introduction & Line Mirror**<br>*(Sidebar: Single-Model, Normal Flow)* | - Introduce **DigitalTwin.ai** and the **Assembly Intelligence Layer (AIL)**.<br>- Highlight that modern plants lose $20,000/min in downtime and 30% of stations lack sensors.<br>- Show the live 40-station Line Mirror running at 60s takt pace. Point out uninstrumented stations (S7, S11) running on **Bayesian Neighbor Inference**. |
| **0:40 – 1:25** | **Flow Brain & Bottleneck Prediction**<br>*(Sidebar: Inject Station 4 Bottleneck)* | - Switch Anomaly Injector to **Station 4 Bottleneck**.<br>- Navigate to **Flow Brain** tab.<br>- Show the **Two-Sided CUSUM chart** detecting tool wear micro-delays 15–20 minutes ahead.<br>- Highlight the automated **Time-to-Overflow alert** predicting line stoppage before buffer saturation. |
| **1:25 – 2:15** | **Defect Radar & 1:10:100 Containment**<br>*(Sidebar: Inject Quality Gate Interception)* | - Switch Anomaly Injector to **Quality Gate Interception**.<br>- Navigate to **Defect Radar** tab.<br>- Show the quarantined vehicle $VH\text{-}0042$ at Quality Gate 1 (S12).<br>- Explain the **Digital Quality Passport** root-cause breakdown (torque + thermal anomalies).<br>- Explain the **1:10:100 Rule**: Catching flaws in-station ($1–$10) vs end-of-line teardown ($1,800) vs field recall ($10,000+). |
| **2:15 – 3:00** | **Stakeholder Views & Enterprise ROI**<br>*(Navigate to Stakeholder Views)* | - Show the tailored tabs for **Floor Supervisor**, **Plant Manager**, and **Executive Leadership**.<br>- Highlight the business impact: **$2.4M projected annual downtime savings**, **78% reduction in bottleneck duration**, and a payback period of **under 1 month**. |

> **Presenter & Evaluator Note:** When evaluating or recording anomaly scenarios (e.g., Station 4 Bottleneck or Quality Gate Interception), clicking **Pause (⏸)** freezes the line in its critical failure state. This allows presenters and judges to freeze-frame and closely examine the station telemetry, CUSUM drift charts, and vehicle risk passports without the conveyor advancing.

---

## Video Demonstration Link

A 3-minute video presentation and technical walkthrough of the prototype is available at:  
`[LINK_TO_YOUTUBE_OR_DRIVE_DEMO_VIDEO]`

---

## Team Details

- **[Team Member 1 (Lead)]** — [College] | [Stream] | [Graduation Year]
- **[Team Member 2]** — [College] | [Stream] | [Graduation Year]

---
*Accenture Innovation Challenge 2026 — Round 2 Prototype Submission*
