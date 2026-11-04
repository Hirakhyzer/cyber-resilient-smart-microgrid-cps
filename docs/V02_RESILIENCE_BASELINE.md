# v0.2 Resilience Screening Baseline

This document records the first compact screening result for the resilience-first v0.2 study. It is a deterministic CI regression baseline, not publication-scale evidence.

## Recorded protocol

- command: `python scripts/run_resilience_experiments.py --ci`;
- seeds: 21 and 22;
- horizon: 240 simulation steps per run;
- scenarios: 11;
- GitHub Actions run: `41784232283`;
- code commit: `dac7c5c6acd09d2a0ef390a699219031c3133a9e`;
- Python 3.10, 3.11, and 3.12 test matrix: successful;
- resilience suite execution: successful on Python 3.12.

The default non-CI study uses five deterministic seeds and a longer horizon.

## Compact resilience results

| Scenario | Service resilience | Critical-load resilience | Minimum service fraction | Islanding service | Unserved energy (kWh) | Minimum SOC |
|---|---:|---:|---:|---:|---:|---:|
| Grid-connected baseline | 1.0000 | 1.0000 | 1.0000 | — | 0.0000 | 0.6500 |
| Short islanding | 1.0000 | 1.0000 | 0.9988 | 0.9999 | 0.0016 | 0.5216 |
| Medium islanding | 1.0000 | 1.0000 | 0.9967 | 0.9999 | 0.0036 | 0.4206 |
| Long islanding | 0.9935 | 1.0000 | 0.7924 | 0.9874 | 1.2039 | 0.3168 |
| Low initial SOC + islanding | 0.8612 | 0.9563 | 0.3211 | 0.4608 | 25.8538 | 0.3000 |
| Reduced battery capacity + islanding | 0.9991 | 1.0000 | 0.7957 | 0.9965 | 0.1671 | 0.3243 |
| Reduced PV + islanding | 1.0000 | 1.0000 | 0.9944 | 0.9998 | 0.0092 | 0.3633 |
| Cloudy islanding | 0.8090 | 0.8534 | 0.1543 | 0.2581 | 35.5694 | 0.6286 |
| High-load islanding | 0.8089 | 0.8992 | 0.2601 | 0.3850 | 38.3315 | 0.6333 |
| Communication-degraded islanding | 1.0000 | 1.0000 | 0.9993 | 1.0000 | 0.0006 | 0.4226 |
| Combined operational stress | 0.5624 | 0.6629 | 0.1177 | 0.2191 | 89.8837 | 0.3500 |

Values are means over the two CI seeds.

## Interpretation

The new study differentiates operating conditions substantially better than the earlier attack-detection-only screen.

### Islanding duration matters

Short and medium islanding remain nearly fully served in the compact protocol, while long islanding begins to expose resource limits: minimum instantaneous service falls to 0.7924 and unserved energy reaches 1.2039 kWh.

### Energy availability dominates difficult cases

Low initial battery SOC has a much larger service effect than moderate battery-capacity or PV-capacity scaling in this compact window. This is a useful sensitivity result, not a universal ranking.

### Renewable and demand disturbances are strong resilience discriminators

Cloudy islanding and high-load islanding both reduce aggregate service resilience to about 0.81, with 35–38 kWh of unserved energy in the compact protocol.

### Combined stress is the hardest current case

The combined resource, communication, renewable, demand, and islanding case produces:

- service resilience: 0.5624;
- critical-load resilience proxy: 0.6629;
- minimum instantaneous service fraction: 0.1177;
- islanding-period service resilience: 0.2191;
- unserved energy: 89.8837 kWh.

This is a more meaningful resilience stress case than a grid-connected attack scenario with perfect service.

### Communication degradation alone is not dominant in this reduced-order case

The communication-degraded islanding case retains essentially full service. This indicates that the current estimator/forecast fallback masks moderate communication impairment effectively under the chosen physical conditions. More severe and bursty communication studies are needed before drawing a broader conclusion.

## Current limitation: restoration is instantaneous

The present reduced-order grid model restores utility support immediately at the configured reconnection step. Consequently, the current recovery-time metric is 0 s in these compact scenarios.

This should **not** be interpreted as evidence of instantaneous real-world restoration. A future resilience model should include an explicit staged restoration process before recovery-time comparisons are treated as meaningful.

## Scientific boundary

These are synthetic reduced-order simulation results. They do not represent utility measurements, protection-system behavior, reliability certification, or operational guarantees.
