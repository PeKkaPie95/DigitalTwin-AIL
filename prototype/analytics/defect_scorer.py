from config import RISK_THRESHOLDS, RISK_COLORS


def get_risk_label(score: float) -> str:
    for label, (lo, hi) in RISK_THRESHOLDS.items():
        if lo <= score < hi:
            return label
    return "critical" if score >= 80 else "normal"


def get_risk_color(score: float) -> str:
    return RISK_COLORS.get(get_risk_label(score), "#06d6a0")


def format_risk_breakdown(vehicle) -> list[dict]:
    """
    Build a human-readable breakdown of why a vehicle's risk score is what it is.
    Returns a list of dicts suitable for display in a table.
    """
    rows = []
    for station_id, reason, contribution in vehicle.risk_breakdown:
        rows.append({
            "Station": f"S{station_id}",
            "Reason": reason,
            "Risk Added": f"+{contribution:.1f}",
        })
    return rows


def generate_risk_explanation(vehicle) -> str:
    """
    Generate a plain-language explanation for a vehicle's risk score.
    This directly addresses the 'explainable AI' requirement.
    """
    if not vehicle.risk_breakdown:
        return f"Vehicle {vehicle.id} has a low risk score with no flagged anomalies."

    lines = [f"**Vehicle {vehicle.id}** ({vehicle.model}) — Risk Score: **{vehicle.accumulated_risk:.1f}/100** ({get_risk_label(vehicle.accumulated_risk).upper()})"]
    lines.append("")
    lines.append("Contributing factors:")

    # Group by station
    from collections import defaultdict
    by_station = defaultdict(list)
    for station_id, reason, contrib in vehicle.risk_breakdown:
        by_station[station_id].append((reason, contrib))

    for station_id in sorted(by_station.keys()):
        items = by_station[station_id]
        total = sum(c for _, c in items)
        reasons_str = "; ".join(r for r, _ in items)
        lines.append(f"- **Station {station_id}** (+{total:.1f}): {reasons_str}")

    if vehicle.flagged_at_gate:
        lines.append(f"\n[FLAGGED] Quarantined for targeted inspection at Quality Gate {vehicle.flagged_at_gate}")

    return "\n".join(lines)
