# v0.2 Baseline Findings

This document records the first **compact CI screening baseline** for the additive v0.2 experimental path. It does not replace the preserved v0.1 baseline and must not be presented as a publication-scale evaluation.

## Frozen screening protocol

- command: `python scripts/run_v02_experiments.py --ci`;
- seeds: 21 and 22;
- horizon: 240 simulation steps per run;
- scenarios: 14;
- total v0.2 runs: 28;
- test status at the recorded baseline: 28 tests passed;
- comparison command: `python scripts/run_v02_comparison.py --steps 240`;
- recorded CI run: `41782783370`;
- code commit used for the table: `ab126242daf3b7b17d732cbfc87b42b93405d07f`.

The default non-CI experiment uses five seeds and a 720-step horizon. Results below are therefore regression-screening evidence, not a substitute for the full study.

## Compact v0.2 results

| Scenario | Recall | F1 | Packet FPR | Benign-step alarm fraction | Service resilience | Critical-load resilience | Unserved energy (kWh) | Mean detection delay (s) |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| Normal | 0.0000 | 0.0000 | **0.0000** | **0.0000** | 1.0000 | 1.0000 | 0.0000 | — |
| Lossy/high-latency | 0.0000 | 0.0000 | **0.0000** | **0.0000** | 1.0000 | 1.0000 | 0.0000 | — |
| SOC spoof | **0.9500** | 0.9744 | **0.0000** | 0.0075 | 1.0000 | 1.0000 | 0.0000 | 240 |
| PV meter FDI | **0.9500** | 0.9620 | 0.0051 | 0.0125 | 1.0000 | 1.0000 | 0.0000 | 240 |
| Load meter FDI | **0.9500** | 0.9620 | 0.0051 | 0.0125 | 1.0000 | 1.0000 | 0.0000 | 240 |
| Voltage spoof | **0.9500** | 0.9744 | **0.0000** | 0.0075 | 1.0000 | 1.0000 | 0.0000 | 240 |
| Replay | **0.9500** | 0.9744 | **0.0000** | 0.0075 | 1.0000 | 1.0000 | 0.0000 | 240 |
| Rewritten replay | **0.9500** | 0.9620 | 0.0051 | 0.0125 | 1.0000 | 1.0000 | 0.0000 | 240 |
| Freeze | **0.5375** | 0.6879 | 0.0051 | 0.0125 | 1.0000 | 1.0000 | 0.0000 | **1230** |
| Cloud transient | 0.0000 | 0.0000 | **0.1983** | 0.0078 | 1.0000 | 1.0000 | 0.0000 | — |
| Load surge | 0.0000 | 0.0000 | **0.1983** | 0.0078 | 1.0000 | 1.0000 | 0.0000 | — |
| Islanding | 0.0000 | 0.0000 | 0.0085 | 0.0063 | 0.9935 | **1.0000** | 1.2039 | — |
| SOC spoof during islanding | **0.9500** | 0.7600 | 0.1117 | 0.0875 | 0.8861 | 0.9879 | 21.2087 | 240 |
| Rewritten replay during islanding | **0.9500** | 0.7600 | 0.1117 | 0.0875 | 0.8898 | 0.9893 | 20.5308 | 240 |

For no-attack scenarios, recall and F1 are zero by definition because there are no positive attack labels. Interpret false-positive and service metrics instead.

## v0.1 versus v0.2 shared-scenario comparison

The shared 240-step comparison produced:

| Scenario | v0.1 recall | v0.2 recall | v0.1 service | v0.2 service | v0.1 unserved kWh | v0.2 unserved kWh |
|---|---:|---:|---:|---:|---:|---:|
| Normal | 0.0000 | 0.0000 | 1.0000 | 1.0000 | 0.0000 | 0.0000 |
| SOC spoof | 0.9500 | 0.9500 | 1.0000 | 1.0000 | 0.0000 | 0.0000 |
| Replay | 0.9500 | 0.9500 | 1.0000 | 1.0000 | 0.0000 | 0.0000 |
| Rewritten replay | **0.0000** | **0.9500** | 1.0000 | 1.0000 | 0.0000 | 0.0000 |
| Islanding | 0.0000 | 0.0000 | 1.0000 | 0.9934 | 0.0000 | 1.2231 |
| SOC spoof during islanding | 0.9500 | 0.9500 | 0.8873 | 0.8873 | 20.9815 | 20.9824 |

The rewritten-replay gain is promising but should not be interpreted alone. v0.2 also removes simulator-assisted controller/twin information, so some service results become less optimistic, particularly in islanding.

## Main findings

### 1. Rewritten replay is no longer the dominant v0.2 blind spot

In the shared compact comparison, rewritten replay rises from 0.0 recall in v0.1 to 0.95 in v0.2. The gain comes from the combination of independent PV/load model residuals, bounded-reordering freshness semantics, and windowed value-dynamics evidence.

This result should be re-evaluated over the full five-seed protocol and additional operating windows before any general claim is made.

### 2. Communication degradation is now separated from replay evidence

The compact lossy/high-latency scenario produces 0.0 packet false-positive rate and 0.0 benign-step alarm fraction. This is a direct improvement over the first v0.2 draft, which incorrectly treated configured delay/reordering as cyber evidence.

The current semantics derive the acceptable age/reordering window from the configured channel latency and jitter. This remains a simulation assumption rather than a universal network model.

### 3. Freeze remains a genuine research weakness

Freeze recall is only 0.5375 and mean detection delay is 1230 s in the compact protocol. This is substantially weaker than the bias/replay scenarios.

Do not tune this result away. It motivates stronger stagnation/change-point statistics, multi-signal temporal consistency, or a better state estimator in future work.

### 4. Legitimate physical disturbances remain difficult to attribute

Cloud and load transients are not cyber attacks, yet the detector produces a packet-level false-positive rate of 0.1983. The low benign-step alarm fraction outside the disturbance window indicates that most of this behavior is tied to the legitimate regime shift itself.

This is a central v0.2 research gap: **detecting inconsistency is easier than determining whether the cause is malicious, physical, or model mismatch**.

### 5. Islanding exposes service realism that v0.1 can hide

The v0.2 islanding run reports service resilience around 0.9935 and approximately 1.20 kWh unserved energy, while the same compact v0.1 comparison reports perfect service. This difference is expected because v0.2 removes hidden plant-SOC fallback and true power-balance input from the controller/twin path.

The critical-load proxy remains at 1.0 in the compact islanding case under the explicit critical-first accounting assumption.

### 6. Combined cyber + islanding stress is substantially harder

Both SOC spoof and rewritten replay during islanding retain 0.95 attack recall, but packet FPR rises to 0.1117 and aggregate service resilience falls to roughly 0.886–0.890. Critical-load resilience remains around 0.988–0.989 under the accounting proxy.

This makes combined cyber/physical stress a stronger discriminator than grid-connected attack detection alone.

## Research gaps to preserve

The v0.2 results identify several useful open problems:

- freeze/stagnation detection with acceptable delay;
- cyberattack versus legitimate physical-disturbance attribution;
- lower false positives during combined islanding and attack;
- uncertainty calibration rather than heuristic uncertainty envelopes;
- stronger state estimation without hidden simulator truth;
- explicit feeder/critical-load models rather than accounting-only critical-service metrics;
- higher-fidelity validation with a documented power-system test case or external simulator.

These gaps are more valuable scientifically than forcing all scenarios to achieve near-perfect scores.
