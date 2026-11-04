from __future__ import annotations

from dataclasses import dataclass
import math
import numpy as np

from .physical.microgrid import MicrogridModel
from .control.energy_manager import EnergyManager
from .control.local_control import trusted_command
from .control.supervisor import ResilienceSupervisor
from .cyber.telemetry import TelemetryPacket
from .cyber.network import NetworkChannel, NetworkConfig
from .cyber.attacks import AttackConfig, apply_attack
from .cyber.freshness import FreshnessMonitor
from .cyber.trust import TrustManager
from .twin.digital_twin import DigitalTwin
from .twin.estimator import TelemetryStateEstimator
from .security.v02_detector import UncertaintyAwareHybridDetector
from .security.invariants import power_balance_residual_kw
from .security.temporal import temporal_score as temporal_score_fn
from .security.temporal_integrity import TemporalIntegrityMonitor
from .security.isolation import isolate_source
from .metrics.cyber import cyber_metrics
from .metrics.electrical import electrical_metrics
from .metrics.resilience import service_resilience
from .metrics.experiments import detection_delay_seconds, supervisor_occupancy


@dataclass(frozen=True)
class PhysicalDisturbanceConfig:
    start_step: int = 10_000
    end_step: int = 10_001
    cloud_factor: float = 1.0
    load_scale: float = 1.0

    def __post_init__(self) -> None:
        if not isinstance(self.start_step, int) or not isinstance(self.end_step, int):
            raise ValueError("disturbance steps must be integers")
        if self.end_step < self.start_step:
            raise ValueError("disturbance end_step must be >= start_step")
        if not math.isfinite(self.cloud_factor) or not 0.0 <= self.cloud_factor <= 1.0:
            raise ValueError("cloud_factor must be finite and in [0, 1]")
        if not math.isfinite(self.load_scale) or self.load_scale < 0.0:
            raise ValueError("load_scale must be finite and non-negative")

    def active(self, step: int) -> bool:
        return self.start_step <= step < self.end_step


@dataclass(frozen=True)
class V02SimulationConfig:
    steps: int = 720
    dt_minutes: float = 1.0
    start_hour: float = 6.0
    seed: int = 21
    grid_disconnect_step: int = -1
    grid_reconnect_step: int = -1
    network: NetworkConfig = NetworkConfig()
    attack: AttackConfig = AttackConfig(start_step=10_000, end_step=10_001)
    disturbance: PhysicalDisturbanceConfig = PhysicalDisturbanceConfig()
    trust_threshold: float = 0.35
    max_control_telemetry_age_steps: int = 3

    def __post_init__(self) -> None:
        if not isinstance(self.steps, int) or self.steps <= 0:
            raise ValueError("steps must be a positive integer")
        if not math.isfinite(self.dt_minutes) or self.dt_minutes <= 0.0:
            raise ValueError("dt_minutes must be finite and positive")
        if not math.isfinite(self.start_hour):
            raise ValueError("start_hour must be finite")
        if not 0.0 <= self.trust_threshold <= 1.0:
            raise ValueError("trust_threshold must be in [0, 1]")
        if not isinstance(self.max_control_telemetry_age_steps, int) or self.max_control_telemetry_age_steps < 0:
            raise ValueError("max_control_telemetry_age_steps must be a non-negative integer")


def run_v02_simulation(config: V02SimulationConfig | None = None):
    """Run the additive v0.2 telemetry-grounded experiment loop.

    Unlike the preserved v0.1 baseline, controller-facing state and twin inputs do
    not fall back to hidden plant SOC or true plant power balance. The controller
    uses delivered telemetry when trusted/fresh enough and otherwise falls back
    to model forecasts plus the estimator state. This function remains a reduced-
    order simulation and is not a deployment controller.
    """
    cfg = config or V02SimulationConfig()
    rng = np.random.default_rng(cfg.seed)
    plant = MicrogridModel()
    ems = EnergyManager()
    net = NetworkChannel(cfg.network)
    twin = DigitalTwin()
    estimator = TelemetryStateEstimator(
        {
            "soc": twin.state.soc,
            "frequency_hz": twin.state.frequency_hz,
            "voltage_pu": twin.state.voltage_pu,
            "pv_kw": plant.pv.available_power_kw(cfg.start_hour),
            "load_kw": plant.loads.demand_kw(cfg.start_hour),
            "grid_kw": 0.0,
        }
    )
    detector = UncertaintyAwareHybridDetector()
    freshness = FreshnessMonitor()
    trust = TrustManager()
    supervisor = ResilienceSupervisor()
    pv_dynamics = TemporalIntegrityMonitor(window=6, stagnation_epsilon=0.05, mismatch_tolerance=2.5)
    load_dynamics = TemporalIntegrityMonitor(window=6, stagnation_epsilon=0.05, mismatch_tolerance=2.5)

    dt_h = cfg.dt_minutes / 60.0
    dt_s = cfg.dt_minutes * 60.0
    last_packet = None
    replay_snapshot = None
    freeze_snapshot = None
    prediction_history: dict[float, dict[str, float]] = {}
    uncertainty_history: dict[float, dict[str, float]] = {}
    detection_labels: list[int] = []
    detection_alarms: list[int] = []
    attack_packets_dropped = 0
    grid_connected = True

    keys = [
        "time_h", "soc_true", "soc_measured", "soc_twin", "soc_control",
        "pv_kw", "pv_measured_kw", "pv_control_kw", "load_kw", "load_measured_kw", "load_control_kw",
        "battery_kw", "grid_kw", "frequency_hz", "frequency_measured_hz", "frequency_twin_hz",
        "voltage_pu", "voltage_measured_pu", "voltage_twin_pu", "unserved_kw", "served_kw",
        "anomaly_score", "anomaly", "attack_active", "disturbance_active", "packet_received",
        "delivered_packet_count", "communication_fault", "telemetry_age_s", "trust_soc", "trust_pv",
        "trust_load", "supervisor_state", "soc_uncertainty",
    ]
    out = {key: [] for key in keys}
    out["dt_h"] = dt_h

    for step in range(cfg.steps):
        if step == cfg.grid_disconnect_step:
            grid_connected = False
        if step == cfg.grid_reconnect_step:
            grid_connected = True

        now_s = step * dt_s
        hour = (cfg.start_hour + step * dt_h) % 24.0
        pv_forecast = plant.pv.available_power_kw(hour)
        load_forecast = plant.loads.demand_kw(hour)
        estimate = estimator.snapshot()
        last_age_s = math.inf if last_packet is None else max(0.0, now_s - last_packet.timestamp_s)
        telemetry_fresh_for_control = last_age_s <= cfg.max_control_telemetry_age_steps * dt_s

        soc_for_control = estimate.state.get("soc", twin.state.soc)
        pv_for_control = (
            estimate.state.get("pv_kw", pv_forecast)
            if telemetry_fresh_for_control and trust.scores["pv_kw"] >= cfg.trust_threshold
            else pv_forecast
        )
        load_for_control = (
            estimate.state.get("load_kw", load_forecast)
            if telemetry_fresh_for_control and trust.scores["load_kw"] >= cfg.trust_threshold
            else load_forecast
        )

        request = ems.dispatch_kw(load_for_control, pv_for_control, soc_for_control, grid_connected, trust.scores)
        request = trusted_command(request, int(supervisor.state))

        disturbance_active = cfg.disturbance.active(step)
        cloud_factor = cfg.disturbance.cloud_factor if disturbance_active else 1.0
        load_scale = cfg.disturbance.load_scale if disturbance_active else 1.0
        state = plant.step(hour, request, dt_h, cloud_factor=cloud_factor, load_scale=load_scale, grid_connected=grid_connected)

        true = {
            "soc": state.battery_soc,
            "pv_kw": state.pv_power_kw,
            "load_kw": state.load_power_kw,
            "battery_kw": state.battery_power_kw,
            "grid_kw": state.grid_power_kw,
            "frequency_hz": state.frequency_hz,
            "voltage_pu": state.voltage_pu,
        }
        measured = dict(true)
        measured["soc"] += rng.normal(0, 0.002)
        measured["pv_kw"] += rng.normal(0, 0.35)
        measured["load_kw"] += rng.normal(0, 0.4)
        measured["frequency_hz"] += rng.normal(0, 0.018)
        measured["voltage_pu"] += rng.normal(0, 0.0025)

        attack_active = cfg.attack.start_step <= step < cfg.attack.end_step
        packet = TelemetryPacket(step, now_s, measured, simulation_attack_label=attack_active)
        if replay_snapshot is None and step == max(1, cfg.attack.start_step - 20):
            replay_snapshot = packet.clone()
        if freeze_snapshot is None and step == cfg.attack.start_step:
            freeze_snapshot = packet.clone()
        attacked = apply_attack(packet, step, cfg.attack, replay_snapshot, freeze_snapshot)
        attacked.simulation_attack_label = attack_active
        if not net.send(attacked) and attack_active:
            attack_packets_dropped += 1
        received = sorted(net.receive(), key=lambda p: (p.timestamp_s, p.seq))

        estimated_balance = 0.0 if grid_connected else pv_for_control + request - load_for_control
        pred = twin.predict(request, estimated_balance, grid_connected, dt_h)
        pred["pv_kw"] = pv_forecast
        pred["load_kw"] = load_forecast
        pred["grid_kw"] = estimate.state.get("grid_kw", 0.0)
        pred_snapshot = estimator.predict(pred)
        prediction_history[now_s] = dict(pred)
        uncertainty_history[now_s] = dict(pred_snapshot.uncertainty)

        communication_fault = len(received) == 0
        step_alarm = False
        step_score = 0.0
        isolated = None
        trust_scores = dict(trust.scores)

        for rx in received:
            pred_for_rx = prediction_history.get(rx.timestamp_s, pred)
            uncertainty_for_rx = uncertainty_history.get(rx.timestamp_s, pred_snapshot.uncertainty)
            fr = freshness.check(rx, now_s)
            temp_score = temporal_score_fn(
                fr.stale_sequence,
                fr.stale_timestamp,
                fr.age_s,
                max_age_s=max(60.0, 3 * dt_s),
            )
            pv_temporal = pv_dynamics.update(rx.values["pv_kw"], pred_for_rx.get("pv_kw", rx.values["pv_kw"]))
            load_temporal = load_dynamics.update(rx.values["load_kw"], pred_for_rx.get("load_kw", rx.values["load_kw"]))
            dynamics_scores = {
                "pv_kw": min(3.0, pv_temporal.score),
                "load_kw": min(3.0, load_temporal.score),
            }
            bal = power_balance_residual_kw(rx.values)
            score, alarm, source_scores = detector.evaluate(
                rx.values,
                pred_for_rx,
                uncertainty_for_rx,
                temp_score,
                bal,
                dynamics_scores=dynamics_scores,
            )
            trust_scores = trust.update(source_scores)
            current_isolated = isolate_source(source_scores)
            if current_isolated is not None:
                isolated = current_isolated
            step_alarm = step_alarm or alarm
            step_score = max(step_score, score)
            detection_labels.append(int(rx.simulation_attack_label))
            detection_alarms.append(int(alarm))

            correction = dict(rx.values)
            if alarm and current_isolated is not None:
                correction.pop(current_isolated, None)
            estimator.correct(correction)

        if received:
            newest = max(received, key=lambda p: (p.timestamp_s, p.seq))
            if last_packet is None or (newest.timestamp_s, newest.seq) >= (last_packet.timestamp_s, last_packet.seq):
                last_packet = newest

        sup = supervisor.update(
            step_alarm,
            step_score,
            isolated,
            grid_connected,
            state.unserved_load_kw,
            communication_fault=communication_fault,
        )

        current_estimate = estimator.snapshot()
        telemetry_age_s = math.nan if last_packet is None else max(0.0, now_s - last_packet.timestamp_s)
        measured_values = last_packet.values if last_packet is not None else {}
        vals = {
            "time_h": hour,
            "soc_true": state.battery_soc,
            "soc_measured": measured_values.get("soc", math.nan),
            "soc_twin": pred["soc"],
            "soc_control": soc_for_control,
            "pv_kw": state.pv_power_kw,
            "pv_measured_kw": measured_values.get("pv_kw", math.nan),
            "pv_control_kw": pv_for_control,
            "load_kw": state.load_power_kw,
            "load_measured_kw": measured_values.get("load_kw", math.nan),
            "load_control_kw": load_for_control,
            "battery_kw": state.battery_power_kw,
            "grid_kw": state.grid_power_kw,
            "frequency_hz": state.frequency_hz,
            "frequency_measured_hz": measured_values.get("frequency_hz", math.nan),
            "frequency_twin_hz": pred["frequency_hz"],
            "voltage_pu": state.voltage_pu,
            "voltage_measured_pu": measured_values.get("voltage_pu", math.nan),
            "voltage_twin_pu": pred["voltage_pu"],
            "unserved_kw": state.unserved_load_kw,
            "served_kw": state.served_load_kw,
            "anomaly_score": step_score,
            "anomaly": int(step_alarm),
            "attack_active": int(attack_active),
            "disturbance_active": int(disturbance_active),
            "packet_received": int(bool(received)),
            "delivered_packet_count": len(received),
            "communication_fault": int(communication_fault),
            "telemetry_age_s": telemetry_age_s,
            "trust_soc": trust_scores["soc"],
            "trust_pv": trust_scores["pv_kw"],
            "trust_load": trust_scores["load_kw"],
            "supervisor_state": int(sup),
            "soc_uncertainty": current_estimate.uncertainty.get("soc", math.nan),
        }
        for key, value in vals.items():
            out[key].append(value)

    for key, value in list(out.items()):
        if isinstance(value, list):
            out[key] = np.asarray(value)
    out["detection_labels"] = np.asarray(detection_labels, dtype=int)
    out["detection_alarms"] = np.asarray(detection_alarms, dtype=int)
    out["attack_packets_dropped"] = int(attack_packets_dropped)
    return out


def summarize_v02(result):
    cyber = cyber_metrics(result["detection_labels"], result["detection_alarms"])
    electrical = electrical_metrics(result)
    samples = int(len(result["anomaly"]))
    packets_delivered = int(np.sum(result["delivered_packet_count"]))
    attack_generated = int(np.sum(result["attack_active"]))
    attack_observed = int(np.sum(result["detection_labels"]))
    attack_delivery_fraction = attack_observed / attack_generated if attack_generated else 0.0
    end_to_end_attack_recall = cyber["tp"] / attack_generated if attack_generated else 0.0
    ages = np.asarray(result["telemetry_age_s"], dtype=float)
    finite_ages = ages[np.isfinite(ages)]
    disturbance = np.asarray(result["disturbance_active"], dtype=bool)
    alarms = np.asarray(result["anomaly"], dtype=bool)
    disturbance_alarm_fraction = float(np.mean(alarms[disturbance])) if np.any(disturbance) else 0.0
    return {
        "samples": samples,
        "anomaly_samples": int(np.sum(result["anomaly"])),
        "max_anomaly_score": float(np.max(result["anomaly_score"])),
        "packets_delivered": packets_delivered,
        "packet_delivery_fraction": packets_delivered / samples,
        "step_receive_fraction": float(np.mean(result["packet_received"])),
        "communication_fault_fraction": float(np.mean(result["communication_fault"])),
        "mean_telemetry_age_s": float(np.mean(finite_ages)) if finite_ages.size else None,
        "attack_packets_generated": attack_generated,
        "attack_packets_observed": attack_observed,
        "attack_packets_dropped": int(result["attack_packets_dropped"]),
        "attack_delivery_fraction": attack_delivery_fraction,
        "end_to_end_attack_recall": end_to_end_attack_recall,
        "detection_delay_s": detection_delay_seconds(result["attack_active"], result["anomaly"], result["dt_h"] * 3600.0),
        "disturbance_alarm_fraction": disturbance_alarm_fraction,
        "service_resilience": service_resilience(result["served_kw"], result["load_kw"]),
        "mean_soc_uncertainty": float(np.nanmean(result["soc_uncertainty"])),
        "min_trust_soc": float(np.min(result["trust_soc"])),
        "min_trust_pv": float(np.min(result["trust_pv"])),
        "min_trust_load": float(np.min(result["trust_load"])),
        "supervisor_occupancy": supervisor_occupancy(result["supervisor_state"]),
        **cyber,
        **electrical,
    }
