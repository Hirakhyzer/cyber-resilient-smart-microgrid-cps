class ExponentialStateEstimator:
    """Small transparent baseline estimator for future EKF/UKF replacement."""
    def __init__(self, alpha: float = 0.25):
        self.alpha = alpha
        self.state: dict[str, float] = {}

    def update(self, measurements: dict[str, float]) -> dict[str, float]:
        for k, v in measurements.items():
            self.state[k] = v if k not in self.state else self.alpha * v + (1 - self.alpha) * self.state[k]
        return dict(self.state)
