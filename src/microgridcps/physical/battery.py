from dataclasses import dataclass

@dataclass(frozen=True)
class BatteryParams:
    capacity_kwh: float = 120.0
    max_charge_kw: float = 45.0
    max_discharge_kw: float = 45.0
    charge_efficiency: float = 0.95
    discharge_efficiency: float = 0.95
    min_soc: float = 0.15
    max_soc: float = 0.95
    initial_soc: float = 0.65

class BatteryModel:
    """Reduced-order energy bucket. Positive power means discharge to the microgrid."""
    def __init__(self, params: BatteryParams | None = None):
        self.params = params or BatteryParams()
        if self.params.capacity_kwh <= 0:
            raise ValueError("capacity_kwh must be positive")
        if not (0 <= self.params.min_soc < self.params.initial_soc <= self.params.max_soc <= 1):
            raise ValueError("invalid SOC limits")
        self.soc = self.params.initial_soc

    def step(self, requested_power_kw: float, dt_h: float) -> float:
        if dt_h <= 0:
            raise ValueError("dt_h must be positive")
        p = min(self.params.max_discharge_kw, max(-self.params.max_charge_kw, requested_power_kw))
        if p >= 0:
            max_energy = max(0.0, (self.soc - self.params.min_soc) * self.params.capacity_kwh)
            max_p_energy = max_energy * self.params.discharge_efficiency / dt_h
            p = min(p, max_p_energy)
            self.soc -= (p / self.params.discharge_efficiency) * dt_h / self.params.capacity_kwh
        else:
            room = max(0.0, (self.params.max_soc - self.soc) * self.params.capacity_kwh)
            max_charge_input = room / (self.params.charge_efficiency * dt_h)
            p = max(p, -max_charge_input)
            self.soc += (-p * self.params.charge_efficiency) * dt_h / self.params.capacity_kwh
        self.soc = min(self.params.max_soc, max(self.params.min_soc, self.soc))
        return p
