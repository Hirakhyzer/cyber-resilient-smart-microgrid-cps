# Benchmark Protocol

For every scenario record: commit SHA, Python/dependency versions, configuration, seed, attack/fault window, network settings, physical parameters, detector thresholds, and command used.

## Evaluation unit

Cyber classification is evaluated on the **exact telemetry observations delivered to the detector**, not by pairing an alarm with the current simulation step. Each synthetic packet carries a simulation-only ground-truth attack label through delay, jitter, replay cloning, and delivery. That label is never used by the detector or controller.

This distinction matters because a delayed packet received at step `t` may have been generated at an earlier step. Comparing its alarm with the attack state at step `t` would misalign ground truth and distort recall.

The benchmark therefore reports both detector and communication behavior:

- `precision`, `recall`, and `F1`: packet-level classification metrics over delivered observations;
- `attack_delivery_fraction`: fraction of generated attack-window packets observed by the detector;
- `end_to_end_attack_recall`: detected attack packets divided by all generated attack-window packets, so communication loss remains visible;
- `packet_delivery_fraction`: delivered packet count divided by generated packet count (one packet is generated per simulation step in v0.1);
- `step_receive_fraction`: fraction of simulation steps in which at least one packet arrives;
- `communication_fault_fraction`: fraction of steps with no newly delivered telemetry;
- `mean_telemetry_age_s`: age of the held controller-facing telemetry.

`packet_delivery_fraction` and `step_receive_fraction` are intentionally different under latency/jitter because multiple queued packets can arrive in one step.

Minimum additional metrics: false alarms, detection delay where well-defined, maximum frequency/voltage deviation, minimum SOC, unserved energy, service resilience, source-trust minima, and supervisor-state occupancy.

Tune thresholds on separate runs from held-out evaluation cases. Do not report simulator output as operational grid measurements.
