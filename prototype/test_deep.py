import sys
sys.path.insert(0, '.')
from simulation.assembly_line import AssemblyLine
from analytics.cusum_detector import calculate_cusum_both, neighbor_inference
from analytics.bottleneck_predictor import predict_bottlenecks
from analytics.defect_scorer import get_risk_label, format_risk_breakdown, generate_risk_explanation

sim = AssemblyLine()
for _ in range(200):
    sim.step()

print(f"Sim State: Time={sim.time}, Active={len(sim.get_active_vehicles())}, Completed={len(sim.completed_vehicles)}, Flagged={len(sim.flagged_vehicles)}")

# Test predictions
preds = predict_bottlenecks(sim.stations)
print(f"Total Predictions: {len(preds)}")
for p in preds:
    assert "station" in p and "severity" in p and "action" in p

# Test vehicles
for v in sim.get_active_vehicles():
    lbl = get_risk_label(v.accumulated_risk)
    expl = generate_risk_explanation(v)
    assert len(lbl) > 0 and len(expl) > 0

# Test neighbor inference on all stations
for sid, st in sim.stations.items():
    if st.cfg["coverage"] == 0:
        inf = neighbor_inference(sim.stations, sid)
        assert "inferred_cycle_time" in inf
        assert "probability_normal" in inf

print("ALL DASHBOARD DATA MODELS TESTED SUCCESSFULLY")
