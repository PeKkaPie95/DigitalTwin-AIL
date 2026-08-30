import sys
sys.path.insert(0, '.')
from simulation.assembly_line import AssemblyLine

sim = AssemblyLine()
for _ in range(100):
    sim.step()

active = sim.get_active_vehicles()
print(f"OK: time={sim.time}, completed={len(sim.completed_vehicles)}, flagged={len(sim.flagged_vehicles)}, active={len(active)}")
print(f"Alerts: {len(sim.alert_log)}")
if active:
    v = active[0]
    print(f"Sample vehicle: {v}")
    print(f"Risk breakdown: {v.risk_breakdown[:3]}")

# Test analytics
from analytics.cusum_detector import calculate_cusum_both, neighbor_inference
from analytics.bottleneck_predictor import predict_bottlenecks
from analytics.defect_scorer import generate_risk_explanation

preds = predict_bottlenecks(sim.stations)
print(f"Bottleneck predictions: {len(preds)}")
for p in preds[:2]:
    print(f"  [{p['severity']}] {p['message']}")

# Test CUSUM
for sid in [1, 10, 20, 30]:
    st = sim.stations[sid]
    if st.cycle_time_history:
        upper, lower, up, down = calculate_cusum_both(st.cycle_time_history)
        print(f"Station {sid}: CUSUM up_drift={up}, down_drift={down}, len={len(upper)}")

# Test neighbor inference
for sid in range(1, 41):
    if sim.stations[sid].cfg["coverage"] == 0:
        inf = neighbor_inference(sim.stations, sid)
        print(f"Station {sid} (no sensor): inferred CT={inf['inferred_cycle_time']}s, P(normal)={inf['probability_normal']}")
        break

# Test risk explanation
if active:
    exp = generate_risk_explanation(active[0])
    print(f"Risk explanation: {exp[:200]}")

print("ALL TESTS PASSED")
