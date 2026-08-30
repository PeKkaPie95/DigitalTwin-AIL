import numpy as np
from config import STATION_CONFIG

def generate_sensor_reading(station_id: int, is_anomaly: bool = False):
    """Generate realistic sensor data for a station based on its coverage level.

    Returns (sensor_dict, anomaly_flags_list).
    """
    cfg = STATION_CONFIG[station_id]
    coverage = cfg["coverage"]
    data = {}
    anomaly_flags = []

    if coverage == 0:
        # No sensors — data will be inferred by the analytics layer
        return data, anomaly_flags

    # ── Torque (partial + full) ──────────────────────────────────────────
    if cfg["torque_spec"] is not None:
        base_torque = np.random.normal(cfg["torque_spec"], 1.5)
        if is_anomaly and np.random.rand() < 0.4:
            deviation = np.random.choice([-1, 1]) * np.random.uniform(5, 12)
            base_torque += deviation
            anomaly_flags.append(
                f"Torque {'above' if deviation > 0 else 'below'} spec by "
                f"{abs(deviation):.1f} Nm at Station {station_id}"
            )
        data["torque_Nm"] = round(base_torque, 2)

    # ── Temperature (full only) ──────────────────────────────────────────
    if coverage >= 2:
        base_temp = np.random.normal(cfg["temp_spec"], cfg["temp_tol"] * 0.3)
        if is_anomaly and np.random.rand() < 0.3:
            spike = np.random.uniform(8, 20)
            base_temp += spike
            anomaly_flags.append(
                f"Temperature spike +{spike:.1f}°C at Station {station_id}"
            )
        data["temperature_C"] = round(base_temp, 2)

    # ── Vibration (full only) ────────────────────────────────────────────
    if coverage >= 2:
        base_vib = np.random.normal(0.5, 0.08)
        if is_anomaly and np.random.rand() < 0.3:
            vib_spike = np.random.uniform(0.8, 2.0)
            base_vib += vib_spike
            anomaly_flags.append(
                f"Vibration elevated (+{vib_spike:.2f} g) at Station {station_id}"
            )
        data["vibration_g"] = round(max(0, base_vib), 3)

    # ── Power draw (partial + full) — proxy signal ───────────────────────
    if coverage >= 1:
        data["power_kW"] = round(np.random.normal(12.0, 1.5), 2)

    return data, anomaly_flags
