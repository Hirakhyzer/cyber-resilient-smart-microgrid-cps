# Resilience Control

The supervisor separates detection from response. States include NORMAL, WATCH, CYBER_ANOMALY, ISOLATE_SOURCE, DEGRADED_OPERATION, ISLANDED, RECOVERY, and EMERGENCY.

The illustrative energy manager uses net load, PV, SOC, grid connection, and trust. If SOC trust becomes very low, battery dispatch can be withheld rather than following compromised state information. Severe cyber states can zero or derate commands in the simulator.

## v0.1 and v0.2

The preserved v0.1 loop remains available for the original baseline.

In the additive v0.2 loop, controller-facing SOC, PV, and load information is derived from the estimator, delivered telemetry, source trust, telemetry age, and model forecasts rather than silently falling back to hidden plant SOC. This makes cyber effects on the control loop more explicit and can make service results less optimistic.

v0.2 also reports aggregate service resilience and a **critical-load resilience proxy**. The proxy assumes aggregate served power is allocated to critical demand first. It does not model feeders, breakers, protection coordination, or an actual prioritized load-shedding controller.

These responses and metrics are research abstractions, not real protection, emergency, restoration, or utility operating procedures.
