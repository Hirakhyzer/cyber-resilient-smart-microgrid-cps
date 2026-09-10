from dataclasses import dataclass
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
from .security.detector import HybridDetector
from .security.invariants import power_balance_residual_kw
from .security.temporal import temporal_score as temporal_score_fn
from .security.isolation import isolate_source
from .metrics.cyber import cyber_metrics
from .metrics.electrical import electrical_metrics
from .metrics.resilience import service_resilience

@dataclass(frozen=True)
class SimulationConfig:
    steps: int = 720
    dt_minutes: float = 1.0
    start_hour: float = 6.0
    seed: int = 21
    grid_disconnect_step: int = -1
    grid_reconnect_step: int = -1
    network: NetworkConfig = NetworkConfig()
    attack: AttackConfig = AttackConfig(start_step=10_000, end_step=10_001)

def run_simulation(config: SimulationConfig | None = None):
    cfg=config or SimulationConfig(); rng=np.random.default_rng(cfg.seed)
    plant=MicrogridModel(); ems=EnergyManager(); net=NetworkChannel(cfg.network); twin=DigitalTwin(); detector=HybridDetector(); freshness=FreshnessMonitor(); trust=TrustManager(); supervisor=ResilienceSupervisor()
    dt_h=cfg.dt_minutes/60.0; last_packet=None; replay_snapshot=None; freeze_snapshot=None; last_command=0.0
    out={k:[] for k in ["time_h","soc_true","soc_measured","soc_twin","pv_kw","load_kw","battery_kw","grid_kw","frequency_hz","frequency_measured_hz","frequency_twin_hz","voltage_pu","voltage_measured_pu","voltage_twin_pu","unserved_kw","served_kw","anomaly_score","anomaly","attack_active","packet_received","delivered_packet_count","communication_fault","telemetry_age_s","trust_soc","trust_pv","trust_load","supervisor_state"]}
    out["dt_h"]=dt_h
    detection_labels=[]; detection_alarms=[]; attack_packets_dropped=0; prediction_history={}
    grid_connected=True
    for step in range(cfg.steps):
        if step==cfg.grid_disconnect_step: grid_connected=False
        if step==cfg.grid_reconnect_step: grid_connected=True
        hour=(cfg.start_hour + step*dt_h)%24.0
        pv_forecast=plant.pv.available_power_kw(hour)
        load_forecast=plant.loads.demand_kw(hour)
        soc_for_control=plant.battery.soc if last_packet is None else last_packet.values.get("soc", plant.battery.soc)
        request=ems.dispatch_kw(load_forecast,pv_forecast,soc_for_control,grid_connected,trust.scores)
        request=trusted_command(request, int(supervisor.state))
        state=plant.step(hour,request,dt_h,grid_connected=grid_connected)
        true={"soc":state.battery_soc,"pv_kw":state.pv_power_kw,"load_kw":state.load_power_kw,"battery_kw":state.battery_power_kw,"grid_kw":state.grid_power_kw,"frequency_hz":state.frequency_hz,"voltage_pu":state.voltage_pu}
        measured=dict(true)
        measured["soc"] += rng.normal(0,0.002)
        measured["pv_kw"] += rng.normal(0,0.35)
        measured["load_kw"] += rng.normal(0,0.4)
        measured["frequency_hz"] += rng.normal(0,0.018)
        measured["voltage_pu"] += rng.normal(0,0.0025)
        attack_active=cfg.attack.start_step <= step < cfg.attack.end_step
        packet=TelemetryPacket(step, step*cfg.dt_minutes*60.0, measured, simulation_attack_label=attack_active)
        if replay_snapshot is None and step==max(1,cfg.attack.start_step-20): replay_snapshot=packet.clone()
        if freeze_snapshot is None and step==cfg.attack.start_step: freeze_snapshot=packet.clone()
        attacked=apply_attack(packet,step,cfg.attack,replay_snapshot,freeze_snapshot)
        # Replay/freeze clones may come from an earlier clean packet. Restore the
        # current simulation ground-truth label after manipulation; the detector
        # never sees or uses this annotation.
        attacked.simulation_attack_label=attack_active
        if not net.send(attacked) and attack_active:
            attack_packets_dropped += 1
        received=net.receive()
        if received:
            # Use the newest delivered observation for the controller-facing held
            # telemetry, while evaluating every delivered observation below.
            last_packet=max(received,key=lambda p:(p.timestamp_s,p.seq))
        active_packet=last_packet or packet
        now_s=step*cfg.dt_minutes*60.0
        pred_balance = state.pv_power_kw + state.battery_power_kw + state.grid_power_kw - state.load_power_kw
        pred=twin.predict(last_command,pred_balance,grid_connected,dt_h)
        prediction_history[now_s]=dict(pred)
        communication_fault=len(received)==0
        step_alarm=False; step_score=0.0; isolated=None
        trust_scores=dict(trust.scores)
        for rx in received:
            # Evaluate each delivered packet against the twin prediction associated
            # with that packet's timestamp. This prevents legitimate latency from
            # creating artificial residuals and keeps labels aligned after jitter.
            pred_for_rx=prediction_history.get(rx.timestamp_s,pred)
            fr=freshness.check(rx, now_s)
            temp_score=temporal_score_fn(fr.stale_sequence,fr.stale_timestamp,fr.age_s,max_age_s=max(60.0,3*cfg.dt_minutes*60.0))
            bal=power_balance_residual_kw(rx.values)
            score,alarm,source_scores=detector.evaluate(rx.values,pred_for_rx,temp_score,bal)
            trust_scores=trust.update(source_scores)
            current_isolated=isolate_source(source_scores)
            if current_isolated is not None: isolated=current_isolated
            step_alarm=step_alarm or alarm; step_score=max(step_score,score)
            detection_labels.append(int(rx.simulation_attack_label)); detection_alarms.append(int(alarm))
        sup=supervisor.update(step_alarm,step_score,isolated,grid_connected,state.unserved_load_kw,communication_fault=communication_fault)
        last_command=state.battery_power_kw
        telemetry_age_s=max(0.0, now_s-active_packet.timestamp_s)
        vals={
            "time_h":hour,"soc_true":state.battery_soc,"soc_measured":active_packet.values["soc"],"soc_twin":pred["soc"],
            "pv_kw":state.pv_power_kw,"load_kw":state.load_power_kw,"battery_kw":state.battery_power_kw,"grid_kw":state.grid_power_kw,
            "frequency_hz":state.frequency_hz,"frequency_measured_hz":active_packet.values["frequency_hz"],"frequency_twin_hz":pred["frequency_hz"],
            "voltage_pu":state.voltage_pu,"voltage_measured_pu":active_packet.values["voltage_pu"],"voltage_twin_pu":pred["voltage_pu"],
            "unserved_kw":state.unserved_load_kw,"served_kw":state.served_load_kw,"anomaly_score":step_score,"anomaly":int(step_alarm),
            "attack_active":int(attack_active),"packet_received":int(bool(received)),"delivered_packet_count":len(received),"communication_fault":int(communication_fault),"telemetry_age_s":telemetry_age_s,
            "trust_soc":trust_scores["soc"],"trust_pv":trust_scores["pv_kw"],"trust_load":trust_scores["load_kw"],"supervisor_state":int(sup),
        }
        for k,v in vals.items(): out[k].append(v)
    for k,v in list(out.items()):
        if isinstance(v,list): out[k]=np.asarray(v)
    out["detection_labels"]=np.asarray(detection_labels,dtype=int)
    out["detection_alarms"]=np.asarray(detection_alarms,dtype=int)
    out["attack_packets_dropped"]=int(attack_packets_dropped)
    return out

def summarize(result):
    cyber=cyber_metrics(result["detection_labels"],result["detection_alarms"]); electrical=electrical_metrics(result)
    samples=int(len(result["anomaly"])); packets_delivered=int(np.sum(result["delivered_packet_count"])); attack_generated=int(np.sum(result["attack_active"])); attack_observed=int(np.sum(result["detection_labels"]))
    attack_delivery_fraction=attack_observed/attack_generated if attack_generated else 0.0
    end_to_end_attack_recall=cyber["tp"]/attack_generated if attack_generated else 0.0
    return {
        "samples":samples,"anomaly_samples":int(np.sum(result["anomaly"])),"max_anomaly_score":float(np.max(result["anomaly_score"])),
        "packets_delivered":packets_delivered,"packet_delivery_fraction":packets_delivered/samples,"step_receive_fraction":float(np.mean(result["packet_received"])),"communication_fault_fraction":float(np.mean(result["communication_fault"])),"mean_telemetry_age_s":float(np.mean(result["telemetry_age_s"])),
        "attack_packets_generated":attack_generated,"attack_packets_observed":attack_observed,"attack_packets_dropped":int(result["attack_packets_dropped"]),"attack_delivery_fraction":attack_delivery_fraction,"end_to_end_attack_recall":end_to_end_attack_recall,
        "service_resilience":service_resilience(result["served_kw"],result["load_kw"]),
        "min_trust_soc":float(np.min(result["trust_soc"])),"min_trust_pv":float(np.min(result["trust_pv"])),"min_trust_load":float(np.min(result["trust_load"])),
        **cyber, **electrical,
    }
