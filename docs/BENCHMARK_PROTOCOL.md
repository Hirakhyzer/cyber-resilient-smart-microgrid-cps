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


## v0.2 additions

The additive v0.2 path retains the packet-aligned cyber labels above and adds:

- `false_positive_rate`: false alarms divided by all delivered benign observations;
- `benign_step_alarm_fraction`: fraction of simulation steps outside both attack and configured physical-disturbance windows that raise an alarm;
- `disturbance_alarm_fraction`: fraction of configured legitimate physical-disturbance steps with an alarm;
- `detection_delay_s`: time from attack-window start to the first step-level alarm, when one occurs;
- `mean_soc_uncertainty`: mean heuristic SOC uncertainty from the transparent v0.2 estimator;
- `supervisor_occupancy`: fraction of steps spent in each supervisor state;
- `critical_load_resilience`: accounting proxy that credits aggregate served power to critical demand first.

The critical-load metric does not imply feeder-level load shedding, relay logic, or protection coordination. The current plant remains a reduced-order single-bus model.

### Versioned comparison

Do not merge v0.1 and v0.2 results into one undifferentiated table. v0.1 is preserved as the original simulator baseline; v0.2 removes simulator-assisted controller/twin information and adds estimation, uncertainty, and temporal-integrity evidence. Changes in scores may therefore reflect improved methodological realism rather than a simple detector improvement.

The compact CI protocol is a regression screen. Publication reporting should use the default multi-seed protocol or a separately declared larger study and should retain weak scenarios instead of retuning on the evaluation set.
