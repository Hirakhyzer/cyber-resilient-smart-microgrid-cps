from __future__ import annotations

import math


def normalized_uncertainty(residual: float, tolerance: float, model_margin: float = 0.25) -> float:
    if not all(math.isfinite(float(v)) for v in (residual, tolerance, model_margin)):
        raise ValueError("residual, tolerance, and model_margin must be finite")
    if tolerance <= 0.0:
        raise ValueError("tolerance must be positive")
    if model_margin < 0.0:
        raise ValueError("model_margin must be non-negative")
    scale = tolerance * (1.0 + model_margin)
    return abs(residual) / scale


def uncertainty_aware_score(residual: float, tolerance: float, state_uncertainty: float = 0.0, model_margin: float = 0.25) -> float:
    """Normalize a residual while explicitly accounting for estimator uncertainty.

    Increasing uncertainty widens the effective tolerance, reducing overconfident
    alarms during missing-data periods. The value remains an interpretable score,
    not a calibrated probability.
    """
    values = (residual, tolerance, state_uncertainty, model_margin)
    if not all(math.isfinite(float(v)) for v in values):
        raise ValueError("uncertainty score inputs must be finite")
    if tolerance <= 0.0:
        raise ValueError("tolerance must be positive")
    if state_uncertainty < 0.0 or model_margin < 0.0:
        raise ValueError("uncertainty and model_margin must be non-negative")
    effective_tolerance = tolerance * (1.0 + model_margin) + state_uncertainty
    return abs(residual) / max(1e-12, effective_tolerance)
