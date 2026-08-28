import json
from pathlib import Path
from microgridcps.simulation import SimulationConfig
from microgridcps.cyber.network import NetworkConfig
from microgridcps.cyber.attacks import AttackConfig

def load_config(path):
    raw=json.loads(Path(path).read_text())
    raw["network"]=NetworkConfig(**raw.get("network",{}))
    raw["attack"]=AttackConfig(**raw.get("attack",{}))
    return SimulationConfig(**raw)
