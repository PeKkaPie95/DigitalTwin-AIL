import uuid
import numpy as np
from config import VEHICLE_MODELS

class Vehicle:
    """Represents a single vehicle moving through the assembly line."""

    _counter = 0

    def __init__(self, start_time: int):
        Vehicle._counter += 1
        self.seq = Vehicle._counter
        self.id = f"VH-{self.seq:04d}"
        self.model = np.random.choice(
            list(VEHICLE_MODELS.keys()),
            p=[v["prob"] for v in VEHICLE_MODELS.values()],
        )
        self.ct_multiplier = VEHICLE_MODELS[self.model]["ct_mult"]
        self.start_time = start_time
        self.current_station = 1
        self.status = "In Progress"        # In Progress | Completed | Flagged | Held
        self.process_history = []           # list of dicts per station
        self.accumulated_risk = 0.0
        self.risk_breakdown = []            # [(station, reason, risk_added), ...]
        self.flagged_at_gate = None

    def add_station_record(self, station_id, cycle_time, sensor_data, risk_added, risk_reasons):
        """Record what happened at a station."""
        self.process_history.append({
            "station": station_id,
            "cycle_time": round(cycle_time, 2),
            "sensor_data": sensor_data,
            "risk_added": round(risk_added, 2),
        })
        self.accumulated_risk = min(100.0, self.accumulated_risk + risk_added)
        for reason in risk_reasons:
            self.risk_breakdown.append((station_id, reason, round(risk_added / max(len(risk_reasons), 1), 2)))

    @property
    def risk_label(self):
        if self.accumulated_risk >= 80:
            return "critical"
        elif self.accumulated_risk >= 60:
            return "high"
        elif self.accumulated_risk >= 30:
            return "elevated"
        return "normal"

    def __repr__(self):
        return f"<Vehicle {self.id} ({self.model}) risk={self.accumulated_risk:.1f} @ S{self.current_station}>"
