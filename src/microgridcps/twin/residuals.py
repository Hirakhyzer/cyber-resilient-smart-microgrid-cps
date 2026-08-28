def compute_residuals(measured: dict[str, float], predicted: dict[str, float]) -> dict[str, float]:
    return {k: measured[k] - predicted[k] for k in predicted if k in measured}
