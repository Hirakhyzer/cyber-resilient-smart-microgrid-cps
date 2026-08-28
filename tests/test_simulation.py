from microgridcps.simulation import SimulationConfig,run_simulation,summarize
from microgridcps.cyber.attacks import AttackConfig

def test_simulation_shapes_and_finite():
    r=run_simulation(SimulationConfig(steps=120)); assert len(r["soc_true"])==120; assert summarize(r)["samples"]==120

def test_soc_spoof_detected():
    r=run_simulation(SimulationConfig(steps=360,attack=AttackConfig(120,240,soc_bias=-0.2))); s=summarize(r); assert s["recall"]>0.5

def test_replay_metadata_attack_detected():
    r=run_simulation(SimulationConfig(steps=360,attack=AttackConfig(120,240,replay=True))); s=summarize(r); assert s["recall"]>0.5
