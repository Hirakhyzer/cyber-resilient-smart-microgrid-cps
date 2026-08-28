# Synthetic Attack / Fault Catalog

| Scenario | Simulator effect | Defensive objective |
|---|---|---|
| SOC spoof | bias reported SOC | BESS state-integrity detection |
| PV FDI | bias reported PV power | DER consistency |
| Load FDI | bias load telemetry | EMS-input integrity |
| Voltage/frequency spoof | bias electrical state | physics residual detection |
| Replay | resend an older packet and metadata | freshness detection |
| Rewritten replay | resend old values with current metadata | physics/temporal research gap |
| Freeze | hold values constant while metadata advances | stagnation/consistency research |
| Loss/delay/jitter | communication degradation | resilient control |

These scenarios operate only on synthetic simulator data.
