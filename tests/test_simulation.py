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

def test_delivery_and_receive_step_metrics_are_not_conflated():
    r=run_simulation(SimulationConfig(steps=120,network=NetworkConfig(loss_probability=0.0,latency_steps=1,jitter_steps=1,seed=8)))
    s=summarize(r)
    assert s["packets_delivered"] == int(r["delivered_packet_count"].sum())
    assert s["packet_delivery_fraction"] == s["packets_delivered"]/120
    assert s["step_receive_fraction"] == float(r["packet_received"].mean())
    assert s["packet_delivery_fraction"] >= s["step_receive_fraction"]

def test_attack_labels_follow_delivered_packets_under_latency():
    r=run_simulation(SimulationConfig(steps=180,network=NetworkConfig(loss_probability=0.0,latency_steps=2,jitter_steps=1,seed=6),attack=AttackConfig(50,100,soc_bias=-0.2)))
    s=summarize(r)
    assert s["attack_packets_generated"] == 50
    assert s["attack_packets_dropped"] == 0
    assert s["attack_packets_observed"] == 50
    assert s["attack_delivery_fraction"] == 1.0
    assert len(r["detection_labels"]) == s["packets_delivered"]
