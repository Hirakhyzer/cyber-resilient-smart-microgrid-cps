# Digital Twin

## Preserved v0.1 baseline

The v0.1 digital twin predicts SOC, voltage, and frequency with a deliberately mismatched reduced-order model. It was designed as an interpretable baseline and remains unchanged for reproducibility.

The v0.1 simulation historically used simulator-accessible information in parts of the twin/controller path. Those semantics are retained only so the original baseline and its published repository history remain reproducible.

## Additive v0.2 path

The v0.2 experiment path is telemetry-grounded:

- controller-facing SOC starts from the twin/estimator state rather than hidden plant SOC;
- missing measurements remain unavailable until a packet is delivered;
- the twin uses controller-available commands, model forecasts, grid-connection state, and estimator state rather than true plant power balance;
- delivered telemetry corrects a transparent state estimator;
- estimator uncertainty expands during prediction-only periods and contracts after measurement updates;
- packet-timestamp-aligned predictions are retained for delayed-observation evaluation.

The v0.2 estimator is a transparent research baseline. It is **not** an EKF, UKF, CKF, unknown-input observer, formally calibrated Bayesian estimator, or certified state estimator.

## Research purpose

The separation between v0.1 and v0.2 is intentional. It permits direct study of how removing simulator-assisted information changes detection and service conclusions.

Future work should evaluate formally specified state estimators, parameter uncertainty, model mismatch, external measurements, and higher-fidelity electrical solvers against the same versioned benchmark protocol.
