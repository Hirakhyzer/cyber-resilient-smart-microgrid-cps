# v0.2 Experimental Protocol

> **Scope note:** this document preserves the telemetry/security robustness study. The primary v0.2 direction is now the resilience-first protocol in [V02_RESILIENCE_EXPERIMENTS.md](V02_RESILIENCE_EXPERIMENTS.md), which emphasizes islanding, resource sufficiency, service continuity, uncertainty, and restoration.

v0.2 is an additive research layer. The preserved v0.1 simulator and benchmark remain available so changes in results can be attributed to explicit methodological changes rather than a silent rewrite of the baseline.

## Research objective

Evaluate whether a telemetry-grounded, uncertainty-aware cyber-resilience loop provides more defensible conclusions than the v0.1 simulator-assisted baseline under cyber attacks, communication degradation, legitimate physical disturbances, islanding, and combined stress.

## Methodological changes relative to v0.1

1. Controller-facing SOC does not fall back to hidden plant SOC when telemetry is unavailable.
2. The digital twin is not driven by true plant power balance. It uses controller-available commands, model forecasts, and estimator state.
3. Missing measurements remain missing in the recorded telemetry fields until a packet is delivered.
4. Delivered measurements correct a transparent state estimator; estimator uncertainty expands during prediction-only periods and contracts after measurement updates.
5. PV and load evidence are scored independently instead of sharing a tied power-balance attribution score.
6. Windowed value-dynamics evidence is added for freeze and metadata-rewritten replay studies.
7. Detection delay, disturbance alarm fraction, estimator uncertainty, and supervisor-state occupancy are recorded in addition to the v0.1 metrics.
8. The primary v0.2 suite is multi-seed rather than a single fixed-seed demonstration.

None of these changes is presented as a formal observer, calibrated probability model, protection algorithm, or deployment-ready control system.

## Scenario families

The default experiment runs five deterministic seeds across:

- normal operation;
- SOC spoofing;
- PV meter false-data injection;
- load meter false-data injection;
- voltage spoofing;
- ordinary replay;
- metadata-rewritten replay;
- sensor freeze;
- lossy/high-latency communication;
- legitimate cloud transient;
- legitimate load surge;
- islanding;
- SOC spoofing during islanding;
- metadata-rewritten replay during islanding.

The cloud and load cases are deliberately labeled as **physical disturbances, not cyber attacks**. Their purpose is to expose cyber/fault attribution weaknesses and false alarms under operating-regime changes.

## Primary metrics

Report, per scenario and across seeds:

- packet-level precision, recall, and F1 over delivered observations;
- end-to-end attack recall including communication loss;
- detection delay when an attack is present and an alarm occurs;
- packet delivery, receive-step, and communication-fault fractions;
- service resilience and unserved energy;
- frequency and voltage deviation;
- source-trust minima;
- estimator uncertainty;
- supervisor-state occupancy;
- disturbance alarm fraction for legitimate non-cyber disturbances.

Mean, population standard deviation, minimum, and maximum are retained for the main scalar metrics. Single-run values must not be presented as population-level evidence.

## v0.1 versus v0.2 comparison

`scripts/run_v02_comparison.py` evaluates the preserved v0.1 and additive v0.2 paths on shared scenarios. This comparison is intended to reveal both improvements and regressions. A lower score in v0.2 is not automatically a failure: removing simulator ground-truth leakage can legitimately make an experiment more difficult while increasing research validity.

## Commands

```bash
python scripts/run_v02_experiments.py
python scripts/run_v02_comparison.py
```

A compact deterministic protocol is executed in CI:

```bash
python scripts/run_v02_experiments.py --ci
python scripts/run_v02_comparison.py --steps 240
```

## Interpretation rules

- Do not tune thresholds on the same runs used for final reporting.
- Do not claim formal uncertainty calibration; the v0.2 uncertainty envelope is an interpretable heuristic.
- Do not treat detection of a physical disturbance as successful cyber detection.
- Separate packet-level detector performance from service-level resilience.
- Preserve weak scenarios such as stealthy replay if they remain weak after methodology corrections.
- Record commit SHA, seeds, configuration, environment, and exact command for publication results.
