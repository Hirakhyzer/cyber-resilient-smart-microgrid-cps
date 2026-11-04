#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path

from microgridcps.cyber.attacks import AttackConfig
from microgridcps.cyber.network import NetworkConfig
from microgridcps.simulation import SimulationConfig, run_simulation, summarize
from microgridcps.v02 import V02SimulationConfig, run_v02_simulation, summarize_v02


def shared_cases(seed: int, steps: int):
    attack_start = max(30, steps // 3)
    attack_end = min(steps - 20, attack_start + max(30, steps // 6))
    island_start = max(20, steps // 4)
    island_end = min(steps - 10, 3 * steps // 4)
    net = NetworkConfig(loss_probability=0.01, latency_steps=1, jitter_steps=1, seed=seed + 100)
    specs = {
        "normal": {"attack": AttackConfig(10_000, 10_001)},
        "soc_spoof": {"attack": AttackConfig(attack_start, attack_end, soc_bias=-0.18)},
        "replay": {"attack": AttackConfig(attack_start, attack_end, replay=True)},
        "rewritten_replay": {"attack": AttackConfig(attack_start, attack_end, replay=True, rewrite_replay_metadata=True)},
        "islanding": {"attack": AttackConfig(10_000, 10_001), "grid_disconnect_step": island_start, "grid_reconnect_step": island_end},
        "soc_spoof_during_islanding": {"attack": AttackConfig(attack_start, attack_end, soc_bias=-0.18), "grid_disconnect_step": island_start, "grid_reconnect_step": island_end},
    }
    cases = {}
    for name, kwargs in specs.items():
        v01 = SimulationConfig(steps=steps, seed=seed, network=net, **kwargs)
        v02 = V02SimulationConfig(steps=steps, seed=seed, network=net, **kwargs)
        cases[name] = (v01, v02)
    return cases


def main() -> None:
    parser = argparse.ArgumentParser(description="Compare preserved v0.1 and additive v0.2 on shared scenarios")
    parser.add_argument("--seed", type=int, default=21)
    parser.add_argument("--steps", type=int, default=360)
    parser.add_argument("--out", type=Path, default=Path("results/v02/comparison.json"))
    args = parser.parse_args()
    if args.steps < 120:
        raise ValueError("steps must be >= 120")

    payload = {"benchmark": "microgrid-v01-v02-comparison", "seed": args.seed, "steps": args.steps, "scenarios": {}}
    print("scenario\tv01_recall\tv02_recall\tv01_service\tv02_service\tv01_unserved\tv02_unserved")
    for name, (v01_cfg, v02_cfg) in shared_cases(args.seed, args.steps).items():
        v01 = summarize(run_simulation(v01_cfg))
        v02 = summarize_v02(run_v02_simulation(v02_cfg))
        payload["scenarios"][name] = {"v0.1": v01, "v0.2": v02}
        print(
            f"{name}\t{v01['recall']:.4f}\t{v02['recall']:.4f}\t"
            f"{v01['service_resilience']:.4f}\t{v02['service_resilience']:.4f}\t"
            f"{v01['unserved_energy_kwh']:.4f}\t{v02['unserved_energy_kwh']:.4f}"
        )

    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
