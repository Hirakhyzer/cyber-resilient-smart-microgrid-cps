# Cyber-Resilient Smart Microgrid CPS

[![CI](https://github.com/Hirakhyzer/cyber-resilient-smart-microgrid-cps/actions/workflows/ci.yml/badge.svg)](https://github.com/Hirakhyzer/cyber-resilient-smart-microgrid-cps/actions/workflows/ci.yml)
![Python](https://img.shields.io/badge/Python-3.10%2B-blue)
![Status](https://img.shields.io/badge/status-research%20prototype-orange)

A reproducible **cybersecurity + cyber-physical systems (CPS)** research platform for smart microgrids with renewable distributed energy resources (DERs). It couples a reduced-order physical microgrid, telemetry/network effects, digital-twin prediction, cyber-physical anomaly detection, source trust, resilient supervision, and energy-management logic.

> **Research/safety boundary:** this repository is a synthetic simulation scaffold. It is not a protection relay, inverter controller, utility EMS, standards-conformance tool, or deployment-ready security product. Default thresholds and electrical parameters are illustrative.

## Core research question

**Can a microgrid preserve critical energy service when telemetry is noisy, delayed, lost, stale, or maliciously manipulated—without blindly trusting every DER measurement?**

```text
PV + Battery + Loads + Utility Grid
              ↓
       Sensors / DER gateway
              ↓
   Synthetic attack / fault effects
              ↓
     Lossy / delayed network
              ↓
        Microgrid Digital Twin
              ↓
 Hybrid physics + temporal detector
              ↓
       Per-source trust scores
              ↓
      Resilience Supervisor
              ↓
       Energy Management
              ↓
      Battery / grid dispatch
              └──────────────→ Microgrid
```

## Implemented in v0.1

### Physical CPS
- single-bus reduced-order microgrid;
- solar PV profile and inverter-limited output;
- battery energy-storage SOC and power limits;
- time-varying critical/non-critical load;
- grid-connected and islanded operation;
- simplified voltage/frequency dynamics;
- served/unserved load and curtailed power accounting.

### Cyber layer
- sequence-numbered timestamped telemetry;
- packet loss, latency, and jitter;
- false-data injection on SOC, PV, load, voltage, and frequency;
- sensor freeze;
- replay with stale metadata;
- harder replay with rewritten metadata;
- deterministic scenario seeds.

### Digital twin + security
- intentionally mismatched reduced-order digital twin;
- SOC, voltage, and frequency residuals;
- power-balance invariant;
- temporal freshness checks;
- persistence-based hybrid detector;
- per-source trust scores;
- suspect-source isolation baseline;
- timestamp-aligned comparison for delayed telemetry.

### Resilient control
Supervisor states include `NORMAL`, `WATCH`, `CYBER_ANOMALY`, `ISOLATE_SOURCE`, `DEGRADED_OPERATION`, `ISLANDED`, `RECOVERY`, and `EMERGENCY`. The illustrative EMS can refuse low-trust SOC information and reduce/zero battery commands under severe cyber evidence. Missing telemetry is treated as a communication condition (`WATCH`) rather than automatically counted as a replay/cyber alarm.

## Quick start

```bash
git clone https://github.com/Hirakhyzer/cyber-resilient-smart-microgrid-cps.git
cd cyber-resilient-smart-microgrid-cps
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -e ".[dev]"
pytest
```

Run a demo:

```bash
python scripts/run_demo.py --config configs/baseline.json --out results/demo
```

Run the scenario suite:

```bash
python scripts/run_scenarios.py
```

Run the compact benchmark:

```bash
python scripts/run_benchmark.py
```

## Research scenarios

| Scenario | Main research target |
|---|---|
| Normal | false-alarm baseline |
| SOC spoof | BESS state integrity |
| PV meter FDI | DER telemetry integrity |
| Load meter FDI | EMS input integrity |
| Voltage spoof | electrical-state consistency |
| Replay | temporal freshness |
| Rewritten replay | stealthier temporal attack |
| Sensor freeze | stale-data behavior |
| Lossy/high-latency network | communication resilience |
| Islanding | service resilience |
| Attack during islanding | coupled cyber/physical stress |

## Metrics

Cyber classification is packet-aligned: an alarm is scored against the ground-truth label of the **delivered telemetry observation that produced it**, rather than against the attack state of the current simulation step. The simulation-only label is not visible to the detector or controller.

The benchmark separates:

- packet-level precision/recall/F1 over delivered observations;
- attack packet delivery and end-to-end attack recall;
- true packet delivery fraction versus fraction of steps with any packet arrival;
- communication-fault fraction and telemetry age;
- electrical frequency/voltage deviation, SOC, and unserved energy;
- source-trust minima, supervisory behavior, and service resilience.

This separation prevents delay/jitter from silently distorting cyber recall and prevents multiple packets arriving in one step from being mistaken for packet loss. See `docs/BENCHMARK_PROTOCOL.md` for definitions.

## Repository map

```text
src/microgridcps/
├── physical/   # PV, BESS, loads, grid, microgrid plant
├── cyber/      # telemetry, network, attacks, freshness, trust
├── twin/       # digital twin, estimator baseline, residuals
├── security/   # detector, invariants, fusion, isolation
├── control/    # EMS, local command guard, supervisor, restoration
├── agents/     # lightweight distributed-agent abstractions
├── metrics/    # cyber, electrical, resilience metrics
└── simulation.py
```

## Standards/research context

The project is informed by NIST OT/DER cybersecurity guidance and the IEEE 1547 family as context for cyber-resilient DER research. It does **not** claim implementation or certification against those standards. See `docs/REFERENCES.md`.

## Scientific integrity

All generated traces are synthetic unless explicitly replaced with externally sourced data. Report the Git commit, configuration, random seed, attack window, network assumptions, detector thresholds, parameter provenance, and held-out evaluation conditions in any publication.

See [Architecture](docs/ARCHITECTURE.md), [Microgrid Model](docs/MICROGRID_MODEL.md), [Digital Twin](docs/DIGITAL_TWIN.md), [Threat Model](docs/THREAT_MODEL.md), [Attack Catalog](docs/ATTACK_CATALOG.md), [Detection Method](docs/DETECTION_METHOD.md), [Resilience Control](docs/RESILIENCE_CONTROL.md), [Benchmark Protocol](docs/BENCHMARK_PROTOCOL.md), [Reproducibility](docs/REPRODUCIBILITY.md), and [Research Roadmap](docs/RESEARCH_ROADMAP.md).
