def restoration_ready(anomaly_free_steps: int, min_steps: int = 5) -> bool:
    return anomaly_free_steps >= min_steps
