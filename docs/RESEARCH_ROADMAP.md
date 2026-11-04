# Research Roadmap

## v0.1 — reproducible reduced-order CPS baseline
Physical DERs, network effects, synthetic attacks/faults, reduced-order digital twin, hybrid detector, trust, supervisor, EMS, packet-aligned metrics, tests, and CI.

## v0.2 — telemetry-grounded temporal integrity and stronger experiments
**Implemented as an additive experimental layer while preserving v0.1.**

Current v0.2 includes:
- controller/twin paths that do not fall back to hidden plant SOC or true plant power balance;
- transparent telemetry state estimation with an explicit uncertainty envelope;
- bounded-reordering freshness semantics derived from the configured channel model;
- independent PV/load residual evidence for clearer source attribution;
- windowed change/stagnation evidence for freeze and metadata-rewritten replay studies;
- detection-delay, false-positive, benign-alarm, uncertainty, supervisor-occupancy, and critical-load service metrics;
- multi-seed cyber, communication, physical-disturbance, islanding, and combined-stress experiments;
- preserved v0.1 versus v0.2 comparison studies.

The current estimator is intentionally transparent and is **not** claimed to be an EKF/UKF or formally calibrated uncertainty model. Remaining v0.2 research includes stronger freeze/change-point detection, cyber-versus-physical disturbance attribution, and estimator calibration. See `V02_EXPERIMENTS.md` and `V02_BASELINE_FINDINGS.md`.

## v0.3 — distributed intelligence
Agent-level local twins/trust, consensus under packet loss, source isolation, decentralized fallback, and explicit studies of distributed evidence disagreement.

## v0.4 — higher-fidelity grid model
Adapter for pandapower/OpenDSS/PyPSA or FMI; documented test-system parameters, parameter mismatch, uncertainty studies, and external-simulator validation.

## v0.5 — security-aware optimization
Constrained EMS/MPC with cyber risk, explicit critical-load preservation, restoration objectives, and comparison against the current rule-based controller.

## v1.0 — reproducible publication artifact
Held-out benchmark suite, documented dataset interface, experiment manifests, stable API, archived release, and publication-scale multi-seed evaluation.
