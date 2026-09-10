from microgridcps.simulation import SimulationConfig,run_simulation,summarize
from microgridcps.cyber.attacks import AttackConfig
from microgridcps.cyber.network import NetworkConfig

def test_simulation_shapes_and_finite():
    r=run_simulation(SimulationConfig(steps=120)); assert len(r["soc_true"])==120; assert summarize(r)["samples"]==120

def test_soc_spoof_detected():
    r=run_simulation(SimulationConfig(steps=360,attack=AttackConfig(120,240,soc_bias=-0.2))); s=summarize(r); assert s["recall"]>0.5

def test_replay_metadata_attack_detected():
    r=run_simulation(SimulationConfig(steps=360,attack=AttackConfig(120,240,replay=True))); s=summarize(r); assert s["recall"]>0.5

def test_total_packet_loss_is_communication_fault_not_cyber_alarm():
    r=run_simulation(SimulationConfig(steps=60,network=NetworkConfig(loss_probability=1.0,latency_steps=0,jitter_steps=0,seed=4)))
    s=summarize(r)
    assert s["communication_fault_fraction"] == 1.0
    assert s["packet_delivery_fraction"] == 0.0
    assert s["fp"] == 0
    assert int(r["anomaly"].sum()) == 0
