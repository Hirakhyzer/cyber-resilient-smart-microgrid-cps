from __future__ import annotations

from collections import deque
from dataclasses import dataclass
import math


@dataclass(frozen=True)
class TemporalIntegrityResult:
    stagnation_score: float
    change_mismatch_score: float
    samples: int

    @property
    def score(self) -> float:
        return max(self.stagnation_score, self.change_mismatch_score)


class TemporalIntegrityMonitor:
    """Windowed value-dynamics monitor for v0.2 replay/freeze experiments.

    It does not declare an attack by itself. Stagnation evidence is intentionally
    conservative: the observed signal must be nearly constant while the expected
    signal changes by more than the configured mismatch tolerance.
    """

    def __init__(self, window: int = 6, stagnation_epsilon: float = 1e-4, mismatch_tolerance: float = 0.02):
        if not isinstance(window, int) or window < 3:
            raise ValueError("window must be an integer >= 3")
        if not math.isfinite(stagnation_epsilon) or stagnation_epsilon <= 0.0:
            raise ValueError("stagnation_epsilon must be finite and positive")
        if not math.isfinite(mismatch_tolerance) or mismatch_tolerance <= 0.0:
            raise ValueError("mismatch_tolerance must be finite and positive")
        self.window = window
        self.stagnation_epsilon = stagnation_epsilon
        self.mismatch_tolerance = mismatch_tolerance
        self.observed: deque[float] = deque(maxlen=window)
        self.predicted: deque[float] = deque(maxlen=window)

    def update(self, observed_value: float, predicted_value: float) -> TemporalIntegrityResult:
        observed = float(observed_value)
        predicted = float(predicted_value)
        if not math.isfinite(observed) or not math.isfinite(predicted):
            return TemporalIntegrityResult(0.0, 0.0, len(self.observed))
        self.observed.append(observed)
        self.predicted.append(predicted)
        if len(self.observed) < 3:
            return TemporalIntegrityResult(0.0, 0.0, len(self.observed))

        obs_range = max(self.observed) - min(self.observed)
        pred_range = max(self.predicted) - min(self.predicted)
        stagnation_score = 0.0
        if obs_range <= self.stagnation_epsilon and pred_range > self.mismatch_tolerance:
            stagnation_score = pred_range / self.mismatch_tolerance

        observed_change = self.observed[-1] - self.observed[-2]
        predicted_change = self.predicted[-1] - self.predicted[-2]
        change_mismatch = abs(observed_change - predicted_change)
        change_mismatch_score = change_mismatch / self.mismatch_tolerance
        return TemporalIntegrityResult(stagnation_score, change_mismatch_score, len(self.observed))
