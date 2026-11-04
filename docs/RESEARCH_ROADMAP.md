# Research Roadmap

## v0.1 — reproducible reduced-order CPS baseline
Physical DERs, network effects, synthetic attacks/faults, reduced-order digital twin, hybrid detector, trust, supervisor, EMS, packet-aligned metrics, tests, and CI.

## v0.2 — resilience, state estimation, and stronger simulation studies
**Implemented as an additive experimental layer while preserving v0.1.**

Primary v0.2 direction:
- telemetry-grounded state estimation with explicit uncertainty;
- reduced-order islanding-duration studies;
- initial-SOC, battery-capacity, and PV-capacity sensitivity experiments;
- cloud and load-variation studies;
- degraded-communication and combined-stress simulation cases;
- aggregate and critical-load service metrics, minimum service fraction, unserved energy, islanding-period performance, and post-reconnection recovery metrics;
- preserved telemetry/security experiments as a secondary robustness layer.

The resource controls are transparent simulation parameters rather than calibrated degradation models. Critical-load service remains an accounting proxy until the reduced-order model includes explicit controllable load classes.

Near-term v0.2 research should prioritize reserve-aware simulation policies, explicit critical/flexible load abstractions, restoration studies, forecast uncertainty, and validation against a documented test system.

## v0.3 — distributed intelligence
Agent-level local twins/trust, consensus under packet loss, source isolation, decentralized fallback, and explicit studies of distributed evidence disagreement.

## v0.4 — higher-fidelity grid model
Adapter for pandapower/OpenDSS/PyPSA or FMI; documented test-system parameters, parameter mismatch, uncertainty studies, and external-simulator validation.

## v0.5 — security-aware optimization
Constrained EMS/MPC with cyber risk, explicit critical-load preservation, restoration objectives, and comparison against the current rule-based controller.

## v1.0 — reproducible publication artifact
Held-out benchmark suite, documented dataset interface, experiment manifests, stable API, archived release, and publication-scale multi-seed evaluation.
