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

## Video Demonstration

A 3-minute video presentation and technical walkthrough of the prototype is available at:  
**[Watch the Prototype Demo Video](https://github.com/PeKkaPie95/DigitalTwin-AIL)** *(Replace with your YouTube / Google Drive link)*

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

## Repository Structure & Detailed File-by-File Breakdown

```
DigitalTwin-AIL/
├── business_proposal.md          # Comprehensive Round 2 Business & Technical Proposal
├── README.md                     # Technical Documentation, File Directory & Evaluation Guide
├── .gitignore                    # Git Ignore Configuration
└── prototype/                    # Interactive Streamlit Prototype Codebase
    ├── app.py                    # Main Entry Point & Dashboard Router
    ├── config.py                 # Factory Model Configuration & Color Constants
    ├── requirements.txt          # Python Package Dependencies
    ├── test_smoke.py             # Rapid Unit & Pipeline Smoke Test Suite
    ├── test_deep.py              # Multi-View Dashboard Integration & Stress Test Suite
    ├── simulation/
    │   ├── __init__.py           # Simulation Package Marker
    │   ├── assembly_line.py      # Discrete-Event 40-Station Manufacturing Engine
    │   ├── vehicle.py            # Vehicle Entity & Digital Quality Passport Dataclass
    │   └── data_generator.py     # Sensor Telemetry Synthesizer & Fault Generator
    ├── analytics/
    │   ├── __init__.py           # Analytics Package Marker
    │   ├── cusum_detector.py     # Two-Sided CUSUM & Bayesian Neighbor Inference Engine
    │   ├── bottleneck_predictor.py # Buffer Fill-Rate Regression & Lookahead Forecaster
    │   └── defect_scorer.py      # Multi-Factor Explainable AI Risk Attribution Model
    └── dashboard/
        ├── __init__.py           # Dashboard Views Package Marker
        ├── line_mirror.py        # Real-Time 40-Station Line Status Visualizer View
        ├── flow_brain_view.py    # Predictive CUSUM Drift & Bottleneck Dashboard View
        ├── defect_radar_view.py  # Vehicle Quality Risk Registry & Passport View
        └── stakeholder_views.py  # Persona Views (Supervisor / Plant Manager / Leadership)
```

### Detailed File Responsibilities

#### Root Directory
* **`business_proposal.md`**: The formal Round 2 competition proposal. Details problem framing across five documented industry failure modes, solution design, technical novelty, target personas, rollout roadmap, and quantified financial ROI ($2.4M/year savings).
* **`README.md`**: Complete repository documentation providing architecture overviews, installation guides, evaluation instructions, and the official 3-minute video presentation script.
* **`.gitignore`**: Excludes virtual environments (`.venv`), Python cache artifacts (`__pycache__`), IDE configurations, and temporary brainstorming materials from git tracking.

#### Core Prototype Modules (`prototype/`)
* **`app.py`**: The Streamlit web application entry point. Injects the custom dark Accenture theme CSS, handles session state, coordinates the continuous simulation playback loop, renders sidebar controls (Fleet Mode, Anomaly Injector, Play/Pause/Reset), and routes between the four dashboard consoles.
* **`config.py`**: Central configuration registry storing factory constants (40 stations, 60-second takt pace, buffer capacity of 5), zone boundaries (Body, Paint, Final), station instrumentation levels (Full/Partial/Inferred), vehicle model multipliers, and enterprise hex color palettes.
* **`requirements.txt`**: Pinned Python package dependencies (`streamlit`, `pandas`, `numpy`, `plotly`, `scipy`).
* **`test_smoke.py`**: Terminal-based test script validating simulation initialization, vehicle step progression, alert creation, and analytics routines.
* **`test_deep.py`**: Stress test suite executing 400 simulation ticks and verifying data contract integrity across all four UI rendering views.

#### Simulation Engine (`prototype/simulation/`)
* **`assembly_line.py`**: The discrete-event manufacturing simulation engine. Manages state for all 40 workstations (`Station` class), controls deterministic vehicle arrival spacing to prevent artificial queuing, executes work cycles, moves vehicles between buffers, evaluates Quality Gate quarantines, and maintains operational history.
* **`vehicle.py`**: The `Vehicle` dataclass representing individual chassis units rolling down the line. Maintains unit identifiers ($VH\text{-}XXXX$), model classes (Sedan/SUV/Truck), station-by-station telemetry timestamps, accumulated risk scores, and root-cause risk logs (**Digital Quality Passport**).
* **`data_generator.py`**: Sensor synthesis engine generating realistic multi-stream physical telemetry (Torque in Nm, Oven Temperature in °C, Structural Vibration in g) with Gaussian noise and probabilistic industrial anomalies.

#### Predictive Analytics Layer (`prototype/analytics/`)
* **`cusum_detector.py`**: Advanced statistical process control implementing **Two-Sided CUSUM (Cumulative Sum)** drift detection ($S_H, S_L$) to catch micro-delays before hard alarms fire. Also contains the **Bayesian Neighbor Inference Engine** that calculates posterior cycle distributions ($P(\text{Normal})$ vs $P(\text{Slow})$) for uninstrumented legacy stations.
* **`bottleneck_predictor.py`**: Linear regression engine analyzing buffer queue depth slopes over rolling time windows, projecting minutes-to-overflow countdowns and downstream station starvation advisories.
* **`defect_scorer.py`**: Explainable AI risk engine combining physical sensor deviations, statistical tool wear factors, and Bayesian uncertainty allowances into a normalized 0–100 vulnerability score with plain-English human explanations.

#### Dashboard Consoles (`prototype/dashboard/`)
* **`line_mirror.py`**: Renders the **Line Mirror** view: live 40-station grid categorized by zone, sensor coverage badges (`[FULL]`, `[PARTIAL]`, `[INFERRED]`), buffer queue gauges, station inspection cards, and cycle time vs. takt trajectory charts.
* **`flow_brain_view.py`**: Renders the **Flow Brain** view: interactive Plotly two-sided CUSUM drift charts with upper/lower decision thresholds, predictive time-to-overflow alert banners, and factory-wide WIP buffer depth bar charts.
* **`defect_radar_view.py`**: Renders the **Defect Radar** view: vehicle risk distribution histograms, sortable vehicle risk table, interactive **Digital Quality Passport** modal with root-cause attribution, and Quality Gate quarantine audit logs.
* **`stakeholder_views.py`**: Renders the **Stakeholder Intelligence** view: tailored role-based tabs for **Floor Supervisors** (tactical triage & dispatch), **Plant Operations Managers** (shift OEE, schedule attainment & Pareto analysis), and **Executive Leadership** (downtime cost savings, warranty reduction & payback analysis).

---
*Accenture Innovation Challenge 2026 — Round 2 Prototype Submission*
