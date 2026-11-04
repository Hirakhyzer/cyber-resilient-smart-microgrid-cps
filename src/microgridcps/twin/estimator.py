from __future__ import annotations

from dataclasses import dataclass, field
import math


class ExponentialStateEstimator:
    """Small transparent baseline estimator retained for v0.1 compatibility."""

    def __init__(self, alpha: float = 0.25):
        if not math.isfinite(alpha) or not 0.0 < alpha <= 1.0:
            raise ValueError("alpha must be finite and in (0, 1]")
        self.alpha = alpha
        self.state: dict[str, float] = {}

    def update(self, measurements: dict[str, float]) -> dict[str, float]:
        for key, value in measurements.items():
            value = float(value)
            if not math.isfinite(value):
                continue
            self.state[key] = value if key not in self.state else self.alpha * value + (1 - self.alpha) * self.state[key]
        return dict(self.state)


@dataclass(frozen=True)
class EstimatorConfig:
    measurement_gain: float = 0.35
    process_uncertainty_growth: float = 0.08
    measurement_uncertainty_decay: float = 0.55
    min_uncertainty: float = 1e-4
    max_uncertainty: float = 10.0

    def __post_init__(self) -> None:
        values = (
            self.measurement_gain,
            self.process_uncertainty_growth,
            self.measurement_uncertainty_decay,
            self.min_uncertainty,
            self.max_uncertainty,
        )
        if not all(math.isfinite(v) for v in values):
            raise ValueError("estimator parameters must be finite")
        if not 0.0 < self.measurement_gain <= 1.0:
            raise ValueError("measurement_gain must be in (0, 1]")
        if self.process_uncertainty_growth < 0.0:
            raise ValueError("process_uncertainty_growth must be non-negative")
        if not 0.0 < self.measurement_uncertainty_decay <= 1.0:
            raise ValueError("measurement_uncertainty_decay must be in (0, 1]")
        if not 0.0 < self.min_uncertainty <= self.max_uncertainty:
            raise ValueError("uncertainty bounds are invalid")


@dataclass
class EstimatorSnapshot:
    state: dict[str, float] = field(default_factory=dict)
    uncertainty: dict[str, float] = field(default_factory=dict)
    measurement_updates: int = 0
    prediction_only_updates: int = 0


class TelemetryStateEstimator:
    """Transparent state estimator for v0.2 telemetry-grounded experiments.

    This is deliberately not presented as an EKF/UKF. It blends model predictions
    with delivered measurements and tracks a simple uncertainty envelope. The
    envelope expands during prediction-only periods and contracts when finite
    measurements arrive. This makes communication gaps explicit without exposing
    hidden simulator truth to the controller-facing state estimate.
    """

    def __init__(self, initial_state: dict[str, float] | None = None, config: EstimatorConfig | None = None):
        self.config = config or EstimatorConfig()
        initial = initial_state or {}
        self.state = {k: float(v) for k, v in initial.items() if math.isfinite(float(v))}
        self.uncertainty = {k: self.config.min_uncertainty for k in self.state}
        self.measurement_updates = 0
        self.prediction_only_updates = 0

    def predict(self, prediction: dict[str, float]) -> EstimatorSnapshot:
        for key, value in prediction.items():
            value = float(value)
            if not math.isfinite(value):
                continue
            self.state[key] = value
            previous = self.uncertainty.get(key, self.config.min_uncertainty)
            self.uncertainty[key] = min(
                self.config.max_uncertainty,
                previous * (1.0 + self.config.process_uncertainty_growth) + self.config.min_uncertainty,
            )
        self.prediction_only_updates += 1
        return self.snapshot()

    def correct(self, measurements: dict[str, float]) -> EstimatorSnapshot:
        updated = False
        gain = self.config.measurement_gain
        for key, raw in measurements.items():
            value = float(raw)
            if not math.isfinite(value):
                continue
            prior = self.state.get(key, value)
            self.state[key] = prior + gain * (value - prior)
            previous = self.uncertainty.get(key, self.config.min_uncertainty)
            self.uncertainty[key] = max(
                self.config.min_uncertainty,
                previous * self.config.measurement_uncertainty_decay,
            )
            updated = True
        if updated:
            self.measurement_updates += 1
        return self.snapshot()

    def snapshot(self) -> EstimatorSnapshot:
        return EstimatorSnapshot(
            state=dict(self.state),
            uncertainty=dict(self.uncertainty),
            measurement_updates=self.measurement_updates,
            prediction_only_updates=self.prediction_only_updates,
        )
