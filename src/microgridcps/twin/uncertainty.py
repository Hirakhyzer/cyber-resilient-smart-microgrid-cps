def normalized_uncertainty(residual: float, tolerance: float, model_margin: float = 0.25) -> float:
    scale = max(1e-9, tolerance * (1.0 + model_margin))
    return abs(residual) / scale
