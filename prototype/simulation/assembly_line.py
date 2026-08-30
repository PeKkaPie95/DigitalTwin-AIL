import numpy as np
from collections import defaultdict
from .vehicle import Vehicle
from .data_generator import generate_sensor_reading
from config import (
    TOTAL_STATIONS, TAKT_TIME, BUFFER_CAPACITY, QUALITY_GATES,
    ANOMALY, STATION_CONFIG, RISK_THRESHOLDS, STATUS_COLORS,
)

TAKT_SCALED = TAKT_TIME / 10.0


class Station:
    """Container for a single workstation on the assembly line."""

    def __init__(self, sid: int):
        self.id = sid
        self.cfg = STATION_CONFIG[sid]
        self.queue: list[Vehicle] = []
        self.current_vehicle: Vehicle | None = None
        self.ticks_in_station = 0
        self.required_time = 0.0
        self.drift_factor = 0.0
        self.cycle_time_history: list[float] = []
        self.queue_depth_history: list[int] = []
        self.status = "Normal"
        self.is_done = False

    def avg_recent_ct(self, n=10):
        if not self.cycle_time_history:
            return TAKT_SCALED
        return float(np.mean(self.cycle_time_history[-n:]))


class AssemblyLine:
    """Discrete-event simulation engine with modular fleet modes and live anomaly injection."""

    MAX_HISTORY = 100

    def __init__(self, fleet_mode="Single-Model (Sedans Only)", anomaly="None (Normal Operation)"):
        self.stations: dict[int, Station] = {i: Station(i) for i in range(1, TOTAL_STATIONS + 1)}
        self.completed_vehicles: list[Vehicle] = []
        self.flagged_vehicles: list[Vehicle] = []
        self.all_vehicles: list[Vehicle] = []
        self.active_alerts: list[dict] = []
        self.alert_log: list[dict] = []
        self.time = 0
        self.total_injected = 0
        self.fleet_mode = fleet_mode
        self.active_anomaly = anomaly

        # Initialize and pre-warm line
        self.rebuild_state(fleet_mode, anomaly)

    def reset_clean(self):
        Vehicle._counter = 0
        self.stations = {i: Station(i) for i in range(1, TOTAL_STATIONS + 1)}
        self.completed_vehicles = []
        self.flagged_vehicles = []
        self.all_vehicles = []
        self.active_alerts = []
        self.alert_log = []
        self.time = 0
        self.total_injected = 0

    def rebuild_state(self, fleet_mode: str, anomaly: str):
        """Warm up the line to t=200 with the chosen fleet mode and inject the chosen anomaly."""
        self.reset_clean()
        self.fleet_mode = fleet_mode
        self.active_anomaly = anomaly

        # Baseline: warm up line with 200 steps so vehicles propagate throughout the factory
        for _ in range(200):
            self._step_internal()

        # Apply specific anomaly state if requested
        self.apply_anomaly(anomaly)

    def apply_anomaly(self, anomaly: str):
        self.active_anomaly = anomaly

        if anomaly == "Station 4 Bottleneck (Tool Wear Drift)":
            st4 = self.stations[4]
            st4.drift_factor = 0.65
            st4.status = "Critical"
            st4.cycle_time_history = [TAKT_SCALED * (1.0 + 0.05 * i) for i in range(15)]
            st4.queue = [Vehicle(start_time=self.time - i) for i in range(5)]
            for v in st4.queue:
                if self.fleet_mode == "Single-Model (Sedans Only)":
                    v.model = "Sedan"
                    v.ct_multiplier = 1.0

            st5 = self.stations[5]
            st5.queue = []
            st5.current_vehicle = None
            st5.status = "Idle"

            self._add_alert(
                "bottleneck",
                "[IMMINENT OVERFLOW] Station 4 buffer saturated (5/5). Line blockage in ~4 min. Upstream cars queued.",
                4,
                "Critical"
            )
            self._add_alert(
                "bottleneck",
                "[STARVATION ADVISORY] Station 5 starved due to Station 4 tool wear bottleneck.",
                5,
                "High"
            )

        elif anomaly == "Sensorless Station 7 (Bayesian Inference)":
            st6 = self.stations[6]
            st7 = self.stations[7]
            st8 = self.stations[8]
            st6.cycle_time_history = [TAKT_SCALED * 1.0] * 15
            st8.cycle_time_history = [TAKT_SCALED * 1.35] * 15
            st7.queue = [Vehicle(start_time=self.time - i) for i in range(3)]
            self._add_alert(
                "sensor",
                "[NEIGHBOR INFERENCE] Station 7 (Sensorless) inferred running 18% above takt via flanking flow differentials.",
                7,
                "Medium"
            )

        elif anomaly == "Quality Gate Interception (1:10:100 Rule)":
            v_flagged = Vehicle(start_time=self.time - 40)
            v_flagged.id = "VH-0042"
            v_flagged.model = "Sedan" if self.fleet_mode == "Single-Model (Sedans Only)" else "SUV"
            v_flagged.add_station_record(
                3, 68.0, {"torque_Nm": 62.4}, 28.5, ["Torque +12.4 Nm above specification at robotic weld fixture"]
            )
            v_flagged.add_station_record(
                8, 71.0, {"temperature_C": 98.2}, 24.0, ["Thermal curing overshoot +13.2 C at seam sealant"]
            )
            v_flagged.add_station_record(
                11, 65.0, {"vibration_g": 1.85}, 18.0, ["High structural vibration resonance during subframe mating"]
            )
            v_flagged.status = "Flagged"
            v_flagged.flagged_at_gate = 12
            self.flagged_vehicles.append(v_flagged)

            self._add_alert(
                "quality",
                "[QUALITY GATE INTERCEPTION] Vehicle VH-0042 quarantined at Gate 1 (Station 12). Risk Score 70.5/100. Saved $1,800 end-of-line teardown.",
                12,
                "High"
            )

        elif anomaly == "None (Normal Operation)":
            for s in self.stations.values():
                s.drift_factor = 0.0
                if s.status in ("Critical", "Blocked"):
                    s.status = "Normal"

    # ────────────────────────── STEP MECHANISM ──────────────────────────
    def step(self):
        self._step_internal()

    def _step_internal(self):
        self.time += 1
        self.active_alerts.clear()
        self._maybe_inject()

        for sid in range(TOTAL_STATIONS, 0, -1):
            self._process_station(sid)

        # Maintain active injected anomaly state continuously across ticks
        if self.active_anomaly == "Station 4 Bottleneck (Tool Wear Drift)":
            self.stations[4].drift_factor = 0.65
        elif self.active_anomaly == "Sensorless Station 7 (Bayesian Inference)":
            self.stations[7].drift_factor = 0.25

        for sid in range(1, TOTAL_STATIONS + 1):
            st = self.stations[sid]
            st.queue_depth_history.append(len(st.queue))
            if len(st.queue_depth_history) > self.MAX_HISTORY:
                st.queue_depth_history.pop(0)

    def _maybe_inject(self):
        st1 = self.stations[1]
        # Target injection rate: Deterministic injection every 7 ticks
        if self.time % (int(TAKT_SCALED) + 1) == 0:
            if len(st1.queue) < BUFFER_CAPACITY:
                v = Vehicle(start_time=self.time)
                if self.fleet_mode == "Single-Model (Sedans Only)":
                    v.model = "Sedan"
                    v.ct_multiplier = 1.0
                st1.queue.append(v)
                self.all_vehicles.append(v)
                self.total_injected += 1

    def _process_station(self, sid: int):
        st = self.stations[sid]

        if np.random.rand() < ANOMALY["drift_onset_prob"]:
            st.drift_factor += ANOMALY["drift_increment"]

        if st.drift_factor > 0:
            st.drift_factor = max(0, st.drift_factor - 0.001)

        if st.current_vehicle is None and st.queue:
            st.current_vehicle = st.queue.pop(0)
            scale = 10.0
            base = (st.cfg["base_cycle_mean"] * st.current_vehicle.ct_multiplier) / scale
            jitter = np.random.normal(0, st.cfg["base_cycle_std"] / scale)
            drift_add = base * st.drift_factor
            st.required_time = max(2, base + jitter + drift_add)
            st.ticks_in_station = 0
            st.is_done = False

        if st.current_vehicle is not None:
            if not st.is_done:
                st.ticks_in_station += 1
                if st.ticks_in_station >= st.required_time:
                    self._complete_math(sid)
                    st.is_done = True
            
            if st.is_done:
                self._attempt_move(sid)

        self._update_status(sid)

    def _complete_math(self, sid: int):
        st = self.stations[sid]
        vehicle = st.current_vehicle
        actual_ct = st.ticks_in_station

        is_anomaly = np.random.rand() < ANOMALY["torque_anomaly_prob"]
        sensor_data, anomaly_flags = generate_sensor_reading(sid, is_anomaly)

        risk_added = 0.0
        risk_reasons = []

        ct_ratio = actual_ct / TAKT_SCALED
        if ct_ratio > 1.15:
            r = (ct_ratio - 1.0) * 10
            risk_added += r
            risk_reasons.append(f"Cycle time {ct_ratio:.0%} of takt pace")

        if "torque_Nm" in sensor_data and st.cfg["torque_spec"]:
            dev = abs(sensor_data["torque_Nm"] - st.cfg["torque_spec"])
            if dev > st.cfg["torque_tol"]:
                r = dev * 0.8
                risk_added += r
                risk_reasons.append(f"Torque deviation {dev:.1f} Nm")

        if "temperature_C" in sensor_data:
            dev = abs(sensor_data["temperature_C"] - st.cfg["temp_spec"])
            if dev > st.cfg["temp_tol"]:
                r = dev * 0.5
                risk_added += r
                risk_reasons.append(f"Temperature deviation {dev:.1f} C")

        if "vibration_g" in sensor_data and sensor_data["vibration_g"] > 1.2:
            r = (sensor_data["vibration_g"] - 0.5) * 5
            risk_added += r
            risk_reasons.append(f"Excess vibration {sensor_data['vibration_g']:.2f} g")

        if st.drift_factor > 0.08:
            risk_added += st.drift_factor * 15
            risk_reasons.append(f"Tool wear factor {st.drift_factor:.2f}")

        if st.cfg["coverage"] == 0:
            risk_added += 2.0
            risk_reasons.append("Sensorless station uncertainty allowance")

        vehicle.add_station_record(sid, actual_ct, sensor_data, risk_added, risk_reasons)

        st.cycle_time_history.append(actual_ct)
        if len(st.cycle_time_history) > self.MAX_HISTORY:
            st.cycle_time_history.pop(0)

        for flag in anomaly_flags:
            self._add_alert("sensor", f"[SENSOR DEVIATION] {flag}", sid, "Medium")

    def _attempt_move(self, sid: int):
        st = self.stations[sid]
        vehicle = st.current_vehicle
        
        if sid in QUALITY_GATES and vehicle.accumulated_risk > RISK_THRESHOLDS["high"][0]:
            vehicle.status = "Flagged"
            vehicle.flagged_at_gate = sid
            self.flagged_vehicles.append(vehicle)
            self._add_alert(
                "quality",
                f"[QUALITY INTERCEPTION] Vehicle {vehicle.id} ({vehicle.model}) intercepted at {QUALITY_GATES[sid]} — Risk {vehicle.accumulated_risk:.1f}/100",
                sid,
                "High",
            )
            st.current_vehicle = None
            st.is_done = False
            return

        if sid == TOTAL_STATIONS:
            vehicle.status = "Completed"
            self.completed_vehicles.append(vehicle)
            st.current_vehicle = None
            st.is_done = False
        else:
            next_st = self.stations[sid + 1]
            if len(next_st.queue) < BUFFER_CAPACITY:
                vehicle.current_station = sid + 1
                next_st.queue.append(vehicle)
                st.current_vehicle = None
                st.is_done = False

    def _update_status(self, sid: int):
        st = self.stations[sid]
        q = len(st.queue)
        avg_ct = st.avg_recent_ct(5)

        if st.current_vehicle is None and q == 0:
            st.status = "Idle"
        elif q >= BUFFER_CAPACITY:
            st.status = "Blocked"
            self._add_alert(
                "bottleneck",
                f"[BUFFER SATURATED] Station {sid} buffer full ({q}/{BUFFER_CAPACITY}). Upstream line blocked.",
                sid,
                "Critical",
            )
        elif q >= BUFFER_CAPACITY - 1:
            st.status = "Critical"
            fill_rate = self._estimate_fill_rate(sid)
            remaining = BUFFER_CAPACITY - q
            mins_to_overflow = max(2, round((remaining / max(0.05, fill_rate)) * (TAKT_SCALED / 60)))
            self._add_alert(
                "bottleneck",
                f"[IMMINENT OVERFLOW] Station {sid} buffer will overflow in ~{mins_to_overflow} min. Queue: {q}/{BUFFER_CAPACITY}.",
                sid,
                "High",
            )
        else:
            # In single model mode, stations stay solid green
            warn_threshold = 1.25 if self.fleet_mode == "Single-Model (Sedans Only)" else 1.10
            if avg_ct > TAKT_SCALED * warn_threshold or q >= 3:
                st.status = "Warning"
            else:
                st.status = "Normal"

    def _estimate_fill_rate(self, sid: int):
        depths = self.stations[sid].queue_depth_history
        if len(depths) < 5:
            return 0.1
        recent = depths[-10:]
        if len(recent) < 2:
            return 0.1
        return max(0.05, (recent[-1] - recent[0]) / len(recent))

    def _add_alert(self, category, message, station, severity):
        alert = {
            "time": self.time,
            "category": category,
            "message": message,
            "station": station,
            "severity": severity,
        }
        self.active_alerts.append(alert)
        self.alert_log.append(alert)
        if len(self.alert_log) > 500:
            self.alert_log = self.alert_log[-500:]

    def get_active_vehicles(self) -> list[Vehicle]:
        vehicles = []
        for st in self.stations.values():
            if st.current_vehicle is not None:
                vehicles.append(st.current_vehicle)
            vehicles.extend(st.queue)
        seen = set()
        unique = []
        for v in vehicles:
            if v.id not in seen:
                seen.add(v.id)
                unique.append(v)
        return unique

    def get_defect_rate(self):
        total = len(self.completed_vehicles) + len(self.flagged_vehicles)
        if total == 0:
            return 0.0
        return len(self.flagged_vehicles) / total * 100
