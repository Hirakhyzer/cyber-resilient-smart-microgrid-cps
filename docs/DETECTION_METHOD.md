# Detection Method

## v0.1 baseline

The preserved baseline detector fuses four interpretable evidence types: digital-twin SOC residual, voltage/frequency residuals, a microgrid power-balance invariant, and telemetry freshness. Evidence is normalized by configurable tolerances and requires persistence before raising an alarm.

Per-source evidence drives trust scores and a simple source-isolation heuristic. The baseline remains available unchanged for comparison.

## v0.2 experimental detector

The additive v0.2 detector extends the transparent baseline with:

- estimator-uncertainty-aware SOC, voltage, and frequency residual scores;
- independent PV and load model residuals instead of assigning the same power-balance score to both sources;
- bounded-reordering freshness semantics based on the configured network jitter window;
- a network-aware telemetry-age budget based on configured latency and jitter;
- conservative windowed stagnation/change evidence for freeze and metadata-rewritten replay studies;
- explicit packet false-positive rate, benign-step alarm fraction, and detection-delay reporting.

The v0.2 detector remains heuristic and interpretable. Its scores are not calibrated probabilities and its persistence rule is not a formal sequential statistical test.

## Current limitations

The compact v0.2 baseline shows that stronger replay sensitivity does not solve attribution. Freeze remains substantially harder to detect, and legitimate cloud/load disturbances can still look anomalous. Combined cyber attack plus islanding also raises false-positive behavior relative to ordinary grid-connected attacks.

These cases are intentionally retained as research gaps rather than hidden by threshold tuning.
