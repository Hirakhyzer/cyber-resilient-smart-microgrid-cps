#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path
from statistics import mean, pstdev

from microgridcps.cyber.network import NetworkConfig
from microgridcps.metrics.resilience import (
    interval_service_resilience,
    interval_unserved_energy_kwh,
    minimum_service_fraction,
    recovery_time_seconds,
)
from microgridcps.v02 import (
    PhysicalDisturbanceConfig,
    ResourceStressConfig,
    V02SimulationConfig,
    run_v02_simulation,
    summarize_v02,
)


def build_resilience_scenarios(seed: int, steps: int) -> dict[str, V02SimulationConfig]:
    island_start = max(30, steps // 4)
    short_reconnect = min(steps - 20, island_start + max(30, steps // 8))
    medium_reconnect = min(steps - 20, island_start + max(60, steps // 4))
    long_reconnect = min(steps - 20, island_start + max(90, steps // 2))
    normal_network = NetworkConfig(loss_probability=0.01, latency_steps=1, jitter_steps=1, seed=seed + 100)

    def base(**kwargs) -> V02SimulationConfig:
        return V02SimulationConfig(steps=steps, seed=seed, network=normal_network, **kwargs)

    return {
        "grid_connected_baseline": base(),
        "short_islanding": base(
            grid_disconnect_step=island_start,
            grid_reconnect_step=short_reconnect,
        ),
        "medium_islanding": base(
            grid_disconnect_step=island_start,
            grid_reconnect_step=medium_reconnect,
        ),
        "long_islanding": base(
            grid_disconnect_step=island_start,
            grid_reconnect_step=long_reconnect,
        ),
        "low_initial_soc_islanding": base(
            grid_disconnect_step=island_start,
            grid_reconnect_step=medium_reconnect,
            resources=ResourceStressConfig(initial_soc=0.30),
        ),
        "reduced_battery_capacity_islanding": base(
            grid_disconnect_step=island_start,
            grid_reconnect_step=medium_reconnect,
            resources=ResourceStressConfig(battery_capacity_scale=0.70),
        ),
        "reduced_pv_islanding": base(
            grid_disconnect_step=island_start,
            grid_reconnect_step=medium_reconnect,
            resources=ResourceStressConfig(pv_capacity_scale=0.70),
        ),
        "cloudy_islanding": base(
            grid_disconnect_step=island_start,
            grid_reconnect_step=medium_reconnect,
            disturbance=PhysicalDisturbanceConfig(
                island_start,
                medium_reconnect,
                cloud_factor=0.45,
                load_scale=1.0,
            ),
        ),
        "high_load_islanding": base(
            grid_disconnect_step=island_start,
            grid_reconnect_step=medium_reconnect,
            disturbance=PhysicalDisturbanceConfig(
                island_start,
                medium_reconnect,
                cloud_factor=1.0,
                load_scale=1.30,
            ),
        ),
        "communication_degraded_islanding": V02SimulationConfig(
            steps=steps,
            seed=seed,
            grid_disconnect_step=island_start,
            grid_reconnect_step=medium_reconnect,
            network=NetworkConfig(
                loss_probability=0.20,
                latency_steps=2,
                jitter_steps=3,
                seed=seed + 200,
            ),
        ),
        "combined_operational_stress": V02SimulationConfig(
            steps=steps,
            seed=seed,
            grid_disconnect_step=island_start,
            grid_reconnect_step=long_reconnect,
            network=NetworkConfig(
                loss_probability=0.15,
                latency_steps=2,
                jitter_steps=2,
                seed=seed + 300,
            ),
            resources=ResourceStressConfig(
                initial_soc=0.35,
                battery_capacity_scale=0.70,
                pv_capacity_scale=0.80,
            ),
            disturbance=PhysicalDisturbanceConfig(
                island_start,
                long_reconnect,
                cloud_factor=0.55,
                load_scale=1.20,
            ),
        ),
    }


def resilience_summary(config: V02SimulationConfig) -> dict:
    result = run_v02_simulation(config)
    summary = summarize_v02(result)

    disconnect = config.grid_disconnect_step
    reconnect = config.grid_reconnect_step
    if 0 <= disconnect < reconnect <= config.steps:
        summary["islanded_service_resilience"] = interval_service_resilience(
            result["served_kw"], result["load_kw"], disconnect, reconnect
        )
        summary["islanded_unserved_energy_kwh"] = interval_unserved_energy_kwh(
            result["unserved_kw"], result["dt_h"], disconnect, reconnect
        )
        summary["recovery_time_s"] = recovery_time_seconds(
            result["served_kw"],
            result["load_kw"],
            reconnect,
            result["dt_h"] * 3600.0,
            threshold=0.99,
            hold_steps=5,
        )
        summary["islanding_duration_min"] = (reconnect - disconnect) * config.dt_minutes
    else:
        summary["islanded_service_resilience"] = None
        summary["islanded_unserved_energy_kwh"] = 0.0
        summary["recovery_time_s"] = None
        summary["islanding_duration_min"] = 0.0

    summary["minimum_service_fraction"] = minimum_service_fraction(
        result["served_kw"], result["load_kw"]
    )
    return summary


def aggregate(rows: list[dict]) -> dict[str, dict[str, float]]:
    metrics = [
        "service_resilience",
        "critical_load_resilience",
        "minimum_service_fraction",
        "unserved_energy_kwh",
        "islanded_service_resilience",
        "islanded_unserved_energy_kwh",
        "recovery_time_s",
        "mean_soc_uncertainty",
        "communication_fault_fraction",
        "max_frequency_deviation_hz",
        "max_voltage_deviation_pu",
        "min_soc",
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
    return output


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Run resilience-first v0.2 smart-microgrid experiments"
    )
    parser.add_argument("--seeds", default="21,22,23,24,25")
    parser.add_argument("--steps", type=int, default=480)
    parser.add_argument("--out", type=Path, default=Path("results/v02-resilience"))
    parser.add_argument("--ci", action="store_true")
    args = parser.parse_args()

    seeds = [21, 22] if args.ci else [int(item.strip()) for item in args.seeds.split(",") if item.strip()]
    steps = 240 if args.ci else args.steps
    if not seeds:
        raise ValueError("at least one seed is required")
    if steps < 180:
        raise ValueError("steps must be >= 180 for the resilience protocol")

    by_scenario: dict[str, list[dict]] = {}
    runs: list[dict] = []
    for seed in seeds:
        for scenario, config in build_resilience_scenarios(seed, steps).items():
            summary = resilience_summary(config)
            runs.append({"scenario": scenario, "seed": seed, **summary})
            by_scenario.setdefault(scenario, []).append(summary)

    aggregates = {name: aggregate(rows) for name, rows in by_scenario.items()}
    payload = {
        "benchmark": "smart-microgrid-v0.2-resilience",
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

    print(
        "scenario\tservice\tcritical_service\tmin_service\tisland_service\t"
        "unserved_kwh\tisland_unserved_kwh\trecovery_s\tmin_soc"
    )
    for name in sorted(aggregates):
        a = aggregates[name]

        def value(metric: str) -> str:
            return f"{a[metric]['mean']:.4f}" if metric in a else "-"

        print(
            f"{name}\t{value('service_resilience')}\t{value('critical_load_resilience')}\t"
            f"{value('minimum_service_fraction')}\t{value('islanded_service_resilience')}\t"
            f"{value('unserved_energy_kwh')}\t{value('islanded_unserved_energy_kwh')}\t"
            f"{value('recovery_time_s')}\t{value('min_soc')}"
        )


if __name__ == "__main__":
    main()
