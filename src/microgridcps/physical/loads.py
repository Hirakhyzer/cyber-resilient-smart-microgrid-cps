from dataclasses import dataclass
import math

@dataclass(frozen=True)
class LoadParams:
    base_kw: float = 35.0
    peak_kw: float = 65.0
    critical_fraction: float = 0.55

class LoadModel:
    def __init__(self, params: LoadParams | None = None):
        self.params = params or LoadParams()
        if not (0.0 < self.params.critical_fraction <= 1.0):
            raise ValueError("critical_fraction must be in (0, 1]")

    def demand_kw(self, hour: float, scale: float = 1.0) -> float:
        morning = math.exp(-0.5 * ((hour - 8.0) / 2.0) ** 2)
        evening = math.exp(-0.5 * ((hour - 19.0) / 2.5) ** 2)
        shape = min(1.0, 0.45 * morning + 0.8 * evening)
        return max(0.0, scale) * (self.params.base_kw + (self.params.peak_kw - self.params.base_kw) * shape)

    def critical_kw(self, total_kw: float) -> float:
        return max(0.0, total_kw) * self.params.critical_fraction
