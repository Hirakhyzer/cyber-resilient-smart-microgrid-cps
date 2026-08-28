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
    out={k:[] for k in ["time_h","soc_true","soc_measured","soc_twin","pv_kw","load_kw","battery_kw","grid_kw","frequency_hz","frequency_measured_hz","frequency_twin_hz","voltage_pu","voltage_measured_pu","voltage_twin_pu","unserved_kw","served_kw","anomaly_score","anomaly","attack_active","packet_received","trust_soc","trust_pv","trust_load","supervisor_state"]}
    out["dt_h"]=dt_h
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
        packet=TelemetryPacket(step, step*cfg.dt_minutes*60.0, measured)
        if replay_snapshot is None and step==max(1,cfg.attack.start_step-20): replay_snapshot=packet.clone()
        if freeze_snapshot is None and step==cfg.attack.start_step: freeze_snapshot=packet.clone()
        attacked=apply_attack(packet,step,cfg.attack,replay_snapshot,freeze_snapshot)
        net.send(attacked); received=net.receive(); rx=received[-1] if received else None
        if rx is not None: last_packet=rx
        active_packet=last_packet or packet
        pred_balance = state.pv_power_kw + state.battery_power_kw + state.grid_power_kw - state.load_power_kw
        pred=twin.predict(last_command,pred_balance,grid_connected,dt_h)
        fr=freshness.check(active_packet, step*cfg.dt_minutes*60.0)
        temp_score=temporal_score_fn(fr.stale_sequence,fr.stale_timestamp,fr.age_s,max_age_s=max(60.0,3*cfg.dt_minutes*60.0))
        bal=power_balance_residual_kw(active_packet.values)
        score,alarm,source_scores=detector.evaluate(active_packet.values,pred,temp_score,bal)
        trust_scores=trust.update(source_scores); isolated=isolate_source(source_scores)
        sup=supervisor.update(alarm,score,isolated,grid_connected,state.unserved_load_kw)
        last_command=state.battery_power_kw
        attack_active=cfg.attack.start_step <= step < cfg.attack.end_step
        vals={
            "time_h":hour,"soc_true":state.battery_soc,"soc_measured":active_packet.values["soc"],"soc_twin":pred["soc"],
            "pv_kw":state.pv_power_kw,"load_kw":state.load_power_kw,"battery_kw":state.battery_power_kw,"grid_kw":state.grid_power_kw,
            "frequency_hz":state.frequency_hz,"frequency_measured_hz":active_packet.values["frequency_hz"],"frequency_twin_hz":pred["frequency_hz"],
            "voltage_pu":state.voltage_pu,"voltage_measured_pu":active_packet.values["voltage_pu"],"voltage_twin_pu":pred["voltage_pu"],
            "unserved_kw":state.unserved_load_kw,"served_kw":state.served_load_kw,"anomaly_score":score,"anomaly":int(alarm),
            "attack_active":int(attack_active),"packet_received":int(rx is not None),"trust_soc":trust_scores["soc"],"trust_pv":trust_scores["pv_kw"],"trust_load":trust_scores["load_kw"],"supervisor_state":int(sup),
        }
        for k,v in vals.items(): out[k].append(v)
    for k,v in list(out.items()):
        if isinstance(v,list): out[k]=np.asarray(v)
    return out

def summarize(result):
    cyber=cyber_metrics(result["attack_active"],result["anomaly"]); electrical=electrical_metrics(result)
    return {
        "samples":int(len(result["anomaly"])),"anomaly_samples":int(np.sum(result["anomaly"])),"max_anomaly_score":float(np.max(result["anomaly_score"])),
        "packet_delivery_fraction":float(np.mean(result["packet_received"])),"service_resilience":service_resilience(result["served_kw"],result["load_kw"]),
        "min_trust_soc":float(np.min(result["trust_soc"])),"min_trust_pv":float(np.min(result["trust_pv"])),"min_trust_load":float(np.min(result["trust_load"])),
        **cyber, **electrical,
    }
