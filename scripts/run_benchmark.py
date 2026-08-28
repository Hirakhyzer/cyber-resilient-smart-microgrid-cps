#!/usr/bin/env python3
import json
from pathlib import Path
from microgridcps.simulation import SimulationConfig,run_simulation,summarize
from microgridcps.cyber.attacks import AttackConfig

cases=[("normal",SimulationConfig()),("soc_spoof",SimulationConfig(attack=AttackConfig(180,300,soc_bias=-0.18))),("replay",SimulationConfig(attack=AttackConfig(180,300,replay=True))),("rewritten_replay",SimulationConfig(attack=AttackConfig(180,300,replay=True,rewrite_replay_metadata=True)))]
out=Path("results/benchmark"); out.mkdir(parents=True,exist_ok=True)
summary={name:summarize(run_simulation(cfg)) for name,cfg in cases}
(out/"summary.json").write_text(json.dumps(summary,indent=2)); print(json.dumps(summary,indent=2))
