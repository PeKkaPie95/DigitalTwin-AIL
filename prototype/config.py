# ============================================================================
# DigitalTwin.ai — Assembly Intelligence Layer (AIL)
# Accenture Innovation Challenge Theme & Configuration
# ============================================================================
import numpy as np

# --- General Production Parameters ---
TAKT_TIME = 60          # seconds — target takt time per station
TOTAL_STATIONS = 40
BUFFER_CAPACITY = 5     # maximum units in buffer queue

# --- Zone Definitions (Accenture Palette) ---
ZONES = {
    "Body Construction":  {"range": (1, 12),  "color": "#A100FF", "tag": "BODY"},
    "Paint Shop":         {"range": (13, 20), "color": "#7500C0", "tag": "PAINT"},
    "Final Assembly":     {"range": (21, 40), "color": "#00E5FF", "tag": "FINAL"},
}

QUALITY_GATES = {
    12: "Gate 1 (Body QG)",
    20: "Gate 2 (Paint QG)",
    40: "Gate 3 (Final QG)",
}

# --- Station Configuration ---
np.random.seed(42)
_raw_coverage = np.random.choice([0, 1, 2], size=TOTAL_STATIONS, p=[0.10, 0.20, 0.70])
for g in QUALITY_GATES:
    _raw_coverage[g - 1] = 2

STATION_CONFIG = {}
for sid in range(1, TOTAL_STATIONS + 1):
    zone_name = None
    for z, info in ZONES.items():
        if info["range"][0] <= sid <= info["range"][1]:
            zone_name = z
            break
    STATION_CONFIG[sid] = {
        "zone": zone_name,
        "coverage": int(_raw_coverage[sid - 1]),          # 0: Inferred, 1: Partial, 2: Full
        "is_quality_gate": sid in QUALITY_GATES,
        "base_cycle_mean": TAKT_TIME,
        "base_cycle_std": 3.0,
        "torque_spec": 50.0 if zone_name != "Paint Shop" else None,
        "torque_tol": 5.0,
        "temp_spec": 85.0 if zone_name != "Paint Shop" else 62.0,
        "temp_tol": 8.0 if zone_name != "Paint Shop" else 3.0,
    }

# --- Vehicle Models ---
VEHICLE_MODELS = {
    "Sedan":  {"prob": 0.50, "ct_mult": 1.00, "color": "#A100FF"},
    "SUV":    {"prob": 0.30, "ct_mult": 1.06, "color": "#00E5FF"},
    "Truck":  {"prob": 0.20, "ct_mult": 1.12, "color": "#FF007F"},
}

# --- Anomaly & Statistical Drift Parameters ---
ANOMALY = {
    "drift_onset_prob": 0.003,
    "drift_increment": 0.04,
    "torque_anomaly_prob": 0.06,
    "temp_spike_prob": 0.04,
    "vibration_anomaly_prob": 0.05,
}

CUSUM_K = 2.0
CUSUM_H = 15.0

# --- Enterprise Color Codes ---
STATUS_COLORS = {
    "Normal": "#00C853",
    "Idle": "#374151",
    "Warning": "#FFB300",
    "Critical": "#FF3D00",
    "Blocked": "#D50000",
}

RISK_THRESHOLDS = {
    "normal":   (0, 30),
    "elevated": (30, 60),
    "high":     (60, 80),
    "critical": (80, 100),
}

RISK_COLORS = {
    "normal":   "#00C853",
    "elevated": "#FFB300",
    "high":     "#FF3D00",
    "critical": "#D50000",
}
