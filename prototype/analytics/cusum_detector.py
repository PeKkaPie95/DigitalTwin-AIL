import numpy as np
from config import CUSUM_K, CUSUM_H


def calculate_cusum(cycle_times: list[float], target: float = 60.0,
                    k: float = CUSUM_K, h: float = CUSUM_H):
    """
    One-sided upper CUSUM for detecting upward drift in cycle times.

    Returns:
        cusum_values: list of CUSUM statistics
        drift_detected: bool — True if threshold h was breached
        breach_index: int | None — first index where drift was detected
    """
    if not cycle_times or len(cycle_times) < 3:
        return [], False, None

    cusum = []
    s = 0.0
    drift_detected = False
    breach_index = None

    for idx, x in enumerate(cycle_times):
        s = max(0.0, s + (x - target - k))
        cusum.append(s)
        if s > h and not drift_detected:
            drift_detected = True
            breach_index = idx

    return cusum, drift_detected, breach_index


def calculate_cusum_both(cycle_times: list[float], target: float = 60.0,
                         k: float = CUSUM_K, h: float = CUSUM_H):
    """
    Two-sided CUSUM: detects both upward drift (slowdown) and downward
    drift (starvation / abnormally fast → possible skipped steps).
    """
    if not cycle_times or len(cycle_times) < 3:
        return [], [], False, False

    upper, lower = [], []
    su, sl = 0.0, 0.0
    up_detected, down_detected = False, False

    for x in cycle_times:
        su = max(0.0, su + (x - target - k))
        sl = max(0.0, sl + (target - k - x))
        upper.append(su)
        lower.append(sl)
        if su > h:
            up_detected = True
        if sl > h:
            down_detected = True

    return upper, lower, up_detected, down_detected


def neighbor_inference(stations_dict, target_sid: int):
    """
    Infer the state of an unmonitored station from its neighbors.

    Returns a dict with estimated metrics and a confidence band.
    """
    prev_sid = target_sid - 1 if target_sid > 1 else None
    next_sid = target_sid + 1 if target_sid < len(stations_dict) else None

    estimates = {}
    sources = []

    for neighbor_sid in [prev_sid, next_sid]:
        if neighbor_sid and neighbor_sid in stations_dict:
            st = stations_dict[neighbor_sid]
            if st.cfg["coverage"] > 0 and st.cycle_time_history:
                sources.append(st.avg_recent_ct(10))

    if sources:
        mean_ct = float(np.mean(sources))
        std_ct = float(np.std(sources)) if len(sources) > 1 else 5.0
        estimates["inferred_cycle_time"] = round(mean_ct, 1)
        estimates["confidence_interval"] = (round(mean_ct - 2 * std_ct, 1),
                                            round(mean_ct + 2 * std_ct, 1))
        estimates["probability_normal"] = round(
            min(1.0, max(0.0, 1 - abs(mean_ct - 60) / 30)), 2
        )
        estimates["probability_slow"] = round(1 - estimates["probability_normal"], 2)
        estimates["method"] = "Neighbor inference"
    else:
        estimates["inferred_cycle_time"] = 60.0
        estimates["confidence_interval"] = (40.0, 80.0)
        estimates["probability_normal"] = 0.5
        estimates["probability_slow"] = 0.5
        estimates["method"] = "Default prior (no neighbor data)"

    return estimates
