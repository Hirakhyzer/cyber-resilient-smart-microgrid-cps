# Digital Twin

The v0.1 digital twin predicts SOC, voltage, and frequency from commanded battery power, observed power balance, connection state, and elapsed time. It intentionally uses slightly different capacity/efficiency/dynamic gains from the plant so normal operation contains model mismatch.

This matters scientifically: a detector that assumes a perfect twin can produce unrealistically optimistic results. Future work should add parameter estimation, uncertainty propagation, EKF/UKF state estimation, and higher-fidelity electrical solvers.
