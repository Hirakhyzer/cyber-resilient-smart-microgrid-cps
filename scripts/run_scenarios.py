#!/usr/bin/env python3
from microgridcps.simulation import SimulationConfig,run_simulation,summarize
from microgridcps.cyber.attacks import AttackConfig
from microgridcps.cyber.network import NetworkConfig

scenarios={
"normal":SimulationConfig(),
"soc_spoof":SimulationConfig(attack=AttackConfig(180,300,soc_bias=-0.18)),
"pv_meter_fdi":SimulationConfig(attack=AttackConfig(180,300,pv_bias_kw=18.0)),
"load_meter_fdi":SimulationConfig(attack=AttackConfig(180,300,load_bias_kw=-15.0)),
"voltage_spoof":SimulationConfig(attack=AttackConfig(180,300,voltage_bias_pu=0.07)),
"replay":SimulationConfig(attack=AttackConfig(180,300,replay=True)),
"rewritten_replay":SimulationConfig(attack=AttackConfig(180,300,replay=True,rewrite_replay_metadata=True)),
"freeze":SimulationConfig(attack=AttackConfig(180,300,freeze=True)),
"lossy_network":SimulationConfig(network=NetworkConfig(loss_probability=0.25,latency_steps=2,jitter_steps=3,seed=13)),
"islanding":SimulationConfig(grid_disconnect_step=240,grid_reconnect_step=480),
"attack_during_islanding":SimulationConfig(grid_disconnect_step=220,grid_reconnect_step=500,attack=AttackConfig(260,360,soc_bias=-0.15)),
}
for name,cfg in scenarios.items():
    print(name, summarize(run_simulation(cfg)))
