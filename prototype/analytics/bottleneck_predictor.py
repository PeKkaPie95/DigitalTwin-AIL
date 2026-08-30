import numpy as np
from config import TAKT_TIME, BUFFER_CAPACITY


def predict_bottlenecks(stations_dict):
    """
    Analyse queue depths and cycle-time trends to predict imminent bottlenecks.

    Returns a list of prediction dicts sorted by severity.
    """
    predictions = []

    for sid, st in stations_dict.items():
        q = len(st.queue)
        avg_ct = st.avg_recent_ct(5)
        recent_depths = st.queue_depth_history[-15:] if st.queue_depth_history else []

        # ── Already overflowing ──────────────────────────────────────────
        if q >= BUFFER_CAPACITY:
            predictions.append({
                "station": sid,
                "zone": st.cfg["zone"],
                "severity": "Critical",
                "queue": q,
                "message": (
                    f"Station {sid} ({st.cfg['zone']}) buffer FULL ({q}/{BUFFER_CAPACITY}). "
                    f"Upstream stations are blocked. Dispatch support immediately."
                ),
                "action": f"Send additional operator to Station {sid}. "
                          f"Consider temporarily diverting vehicles at upstream junction.",
                "eta_minutes": 0,
            })
            continue

        # ── Queue trending upward ────────────────────────────────────────
        if len(recent_depths) >= 5:
            slope = np.polyfit(range(len(recent_depths)), recent_depths, 1)[0]
            if slope > 0.05 and q >= 2:
                remaining_cap = BUFFER_CAPACITY - q
                if slope > 0:
                    ticks_to_full = remaining_cap / slope
                    eta_minutes = round(ticks_to_full * (TAKT_TIME / 60), 1)
                else:
                    eta_minutes = 999

                severity = "High" if eta_minutes < 15 else "Medium"

                predictions.append({
                    "station": sid,
                    "zone": st.cfg["zone"],
                    "severity": severity,
                    "queue": q,
                    "message": (
                        f"Station {sid} ({st.cfg['zone']}) buffer filling — "
                        f"queue {q}/{BUFFER_CAPACITY}, trending up. "
                        f"Estimated overflow in ~{eta_minutes:.0f} min at current rate."
                    ),
                    "action": (
                        f"Monitor Station {sid}. If trend continues for 5 more minutes, "
                        f"consider pre-positioning an extra operator."
                    ),
                    "eta_minutes": eta_minutes,
                })
                continue

        # ── Cycle time above takt ────────────────────────────────────────
        if avg_ct > TAKT_TIME * 1.15 and q >= 1:
            over_pct = ((avg_ct / TAKT_TIME) - 1) * 100
            predictions.append({
                "station": sid,
                "zone": st.cfg["zone"],
                "severity": "Medium",
                "queue": q,
                "message": (
                    f"Station {sid} ({st.cfg['zone']}) running {over_pct:.0f}% above takt. "
                    f"Current avg cycle time {avg_ct:.1f}s vs {TAKT_TIME}s target."
                ),
                "action": (
                    f"Check Station {sid} for tool calibration or operator assistance needs."
                ),
                "eta_minutes": 30,
            })

        # ── Starvation (downstream idle) ─────────────────────────────────
        if q == 0 and st.status == "Idle" and st.cycle_time_history:
            predictions.append({
                "station": sid,
                "zone": st.cfg["zone"],
                "severity": "Low",
                "queue": q,
                "message": (
                    f"Station {sid} ({st.cfg['zone']}) starving — empty queue. "
                    f"Likely caused by upstream delay."
                ),
                "action": f"Check upstream stations ({max(1, sid-3)} – {sid-1}) for blockage.",
                "eta_minutes": None,
            })

    # Sort by severity
    order = {"Critical": 0, "High": 1, "Medium": 2, "Low": 3}
    predictions.sort(key=lambda p: order.get(p["severity"], 4))
    return predictions
