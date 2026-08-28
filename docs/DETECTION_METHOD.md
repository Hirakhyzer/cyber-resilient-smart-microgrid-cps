# Detection Method

The baseline detector fuses four interpretable evidence types: digital-twin SOC residual, voltage/frequency residuals, a microgrid power-balance invariant, and telemetry freshness. Evidence is normalized by configurable tolerances and requires persistence before raising an alarm.

Per-source evidence also drives trust scores and a simple source-isolation heuristic. This is deliberately transparent and should be compared against later statistical, model-based, physics-informed ML, or formally verified alternatives.

Evaluation must report false positives and detection delay, not just whether a scenario is eventually detected.
