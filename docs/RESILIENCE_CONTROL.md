# Resilience Control

The supervisor separates detection from response. States include NORMAL, WATCH, CYBER_ANOMALY, ISOLATE_SOURCE, DEGRADED_OPERATION, ISLANDED, RECOVERY, and EMERGENCY.

The illustrative energy manager uses net load, PV, SOC, grid connection, and trust. If SOC trust becomes very low, battery dispatch can be withheld rather than following compromised state information. Severe cyber states can zero or derate commands in the simulator.

These responses are research abstractions, not real protection or emergency procedures.
