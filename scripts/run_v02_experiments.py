#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path
from statistics import mean, pstdev

from microgridcps.cyber.attacks import AttackConfig
from microgridcps.cyber.network import NetworkConfig
from microgridcps.v02 import (
    PhysicalDisturbanceConfig,
    V02SimulationConfig,
    run_v02_simulation,
    summarize_v02,
)


def build_scenarios(seed: int, steps: int) -> dict[str, V02SimulationConfig]:
    attack_start = max(30, steps // 3)
    attack_end = min(steps - 20, attack_start + max(30, steps // 6))
    island_start = max(20, steps // 4)
    island_end = min(steps - 10, 3 * steps // 4)
    disturbance_start = max(25, steps // 3)
    disturbance_end = min(steps - 15, disturbance_start + max(30, steps // 5))
    normal_net = NetworkConfig(loss_probability=0.01, latency_steps=1, jitter_steps=1, seed=seed + 100)

    def base(**kwargs) -> V02SimulationConfig:
        return V02SimulationConfig(steps=steps, seed=seed, network=normal_net, **kwargs)

    return {
        "normal": base(),
        "soc_spoof": base(attack=AttackConfig(attack_start, attack_end, soc_bias=-0.18)),
        "pv_meter_fdi": base(attack=AttackConfig(attack_start, attack_end, pv_bias_kw=18.0)),
        "load_meter_fdi": base(attack=AttackConfig(attack_start, attack_end, load_bias_kw=-15.0)),
        "voltage_spoof": base(attack=AttackConfig(attack_start, attack_end, voltage_bias_pu=0.07)),
        "replay": base(attack=AttackConfig(attack_start, attack_end, replay=True)),
        "rewritten_replay": base(attack=AttackConfig(attack_start, attack_end, replay=True, rewrite_replay_metadata=True)),
        "freeze": base(attack=AttackConfig(attack_start, attack_end, freeze=True)),
        "lossy_high_latency": V02SimulationConfig(
            steps=steps,
            seed=seed,
            network=NetworkConfig(loss_probability=0.25, latency_steps=2, jitter_steps=3, seed=seed + 200),
        ),
        "cloud_transient": base(
            disturbance=PhysicalDisturbanceConfig(disturbance_start, disturbance_end, cloud_factor=0.45, load_scale=1.0)
        ),
        "load_surge": base(
            disturbance=PhysicalDisturbanceConfig(disturbance_start, disturbance_end, cloud_factor=1.0, load_scale=1.25)
        ),
        "islanding": base(grid_disconnect_step=island_start, grid_reconnect_step=island_end),
        "soc_spoof_during_islanding": base(
            grid_disconnect_step=island_start,
            grid_reconnect_step=island_end,
            attack=AttackConfig(attack_start, attack_end, soc_bias=-0.18),
        ),
        "rewritten_replay_during_islanding": base(
            grid_disconnect_step=island_start,
            grid_reconnect_step=island_end,
            attack=AttackConfig(attack_start, attack_end, replay=True, rewrite_replay_metadata=True),
        ),
    }


def aggregate(rows: list[dict]) -> dict[str, dict[str, float]]:
    metrics = [
        "precision",
        "recall",
        "f1",
        "end_to_end_attack_recall",
        "service_resilience",
        "unserved_energy_kwh",
        "communication_fault_fraction",
        "disturbance_alarm_fraction",
        "mean_soc_uncertainty",
    ]
    output: dict[str, dict[str, float]] = {}
    for metric in metrics:
        values = [float(row[metric]) for row in rows if row.get(metric) is not None]
        if values:
            output[metric] = {
                "mean": mean(values),
                "std": pstdev(values) if len(values) > 1 else 0.0,
                "min": min(values),
                "max": max(values),
            }
    delays = [float(row["detection_delay_s"]) for row in rows if row.get("detection_delay_s") is not None]
    if delays:
        output["detection_delay_s"] = {
            "mean": mean(delays),
            "std": pstdev(delays) if len(delays) > 1 else 0.0,
            "min": min(delays),
            "max": max(delays),
        }
    return output


def main() -> None:
    parser = argparse.ArgumentParser(description="Run the additive v0.2 multi-seed microgrid experiment suite")
    parser.add_argument("--seeds", default="21,22,23,24,25", help="comma-separated deterministic seeds")
    parser.add_argument("--steps", type=int, default=720)
    parser.add_argument("--out", type=Path, default=Path("results/v02"))
    parser.add_argument("--ci", action="store_true", help="use a compact deterministic CI protocol")
    args = parser.parse_args()

    seeds = [21, 22] if args.ci else [int(item.strip()) for item in args.seeds.split(",") if item.strip()]
    steps = 240 if args.ci else args.steps
    if not seeds:
        raise ValueError("at least one seed is required")
    if steps < 120:
        raise ValueError("steps must be >= 120 for the v0.2 experiment protocol")

    by_scenario: dict[str, list[dict]] = {}
    runs: list[dict] = []
    for seed in seeds:
        for name, config in build_scenarios(seed, steps).items():
            summary = summarize_v02(run_v02_simulation(config))
            row = {"scenario": name, "seed": seed, **summary}
            runs.append(row)
            by_scenario.setdefault(name, []).append(summary)

    aggregates = {name: aggregate(rows) for name, rows in by_scenario.items()}
    payload = {
        "benchmark": "microgrid-v0.2-multiseed",
        "protocol_version": "0.2.0",
        "steps": steps,
        "seeds": seeds,
        "scenario_count": len(by_scenario),
        "run_count": len(runs),
        "aggregates": aggregates,
        "runs": runs,
    }

    args.out.mkdir(parents=True, exist_ok=True)
    (args.out / "summary.json").write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")

    print("scenario\trecall_mean\tf1_mean\tservice_mean\tunserved_kwh_mean\tdelay_s_mean")
    for name in sorted(aggregates):
        a = aggregates[name]
        def value(metric: str) -> str:
            return f"{a[metric]['mean']:.4f}" if metric in a else "-"
        print(
            f"{name}\t{value('recall')}\t{value('f1')}\t{value('service_resilience')}\t"
            f"{value('unserved_energy_kwh')}\t{value('detection_delay_s')}"
        )


if __name__ == "__main__":
    main()
