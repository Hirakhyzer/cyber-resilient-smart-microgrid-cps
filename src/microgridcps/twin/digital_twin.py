from dataclasses import dataclass

@dataclass
class TwinState:
    soc: float = 0.63
    frequency_hz: float = 50.0
    voltage_pu: float = 1.0

class DigitalTwin:
    """Reduced-order predictor with intentional small model mismatch."""
    def __init__(self, capacity_kwh: float = 118.0):
        self.capacity_kwh = capacity_kwh
        self.state = TwinState()

    def predict(self, battery_power_kw: float, power_balance_kw: float, grid_connected: bool, dt_h: float) -> dict[str, float]:
        p = battery_power_kw
        eta = 0.94
        if p >= 0:
            self.state.soc -= (p / eta) * dt_h / self.capacity_kwh
        else:
            self.state.soc += (-p * eta) * dt_h / self.capacity_kwh
        self.state.soc = min(1.0, max(0.0, self.state.soc))
        if grid_connected:
            target_f = 50.0 + 0.0015 * power_balance_kw
            target_v = 1.0 + 0.00025 * power_balance_kw
        else:
            target_f = 50.0 + 0.016 * power_balance_kw
            target_v = 1.0 + 0.0022 * power_balance_kw
        self.state.frequency_hz += 0.32 * (target_f - self.state.frequency_hz)
        self.state.voltage_pu += 0.32 * (target_v - self.state.voltage_pu)
        return {"soc": self.state.soc, "frequency_hz": self.state.frequency_hz, "voltage_pu": self.state.voltage_pu}
