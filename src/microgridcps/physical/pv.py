from dataclasses import dataclass
import math

@dataclass(frozen=True)
class PVParams:
    capacity_kw: float = 60.0
    inverter_efficiency: float = 0.97

class PVModel:
    def __init__(self, params: PVParams | None = None):
        self.params = params or PVParams()
        if self.params.capacity_kw <= 0:
            raise ValueError("capacity_kw must be positive")

    def irradiance_pu(self, hour: float) -> float:
        # Smooth illustrative daytime profile; not a solar-resource model.
        phase = (hour - 6.0) / 12.0 * math.pi
        return max(0.0, math.sin(phase)) if 6.0 <= hour <= 18.0 else 0.0

    def available_power_kw(self, hour: float, cloud_factor: float = 1.0) -> float:
        cloud = min(1.0, max(0.0, cloud_factor))
        return self.params.capacity_kw * self.params.inverter_efficiency * self.irradiance_pu(hour) * cloud
