from dataclasses import dataclass

@dataclass(frozen=True)
class EnergyManagerConfig:
    grid_peak_threshold_kw: float = 45.0
    reserve_soc: float = 0.30
    target_soc: float = 0.60
    max_battery_kw: float = 40.0

class EnergyManager:
    """Illustrative dispatch policy; not an optimal-power-flow or real EMS."""
    def __init__(self, config: EnergyManagerConfig | None = None):
        self.config = config or EnergyManagerConfig()

    def dispatch_kw(self, load_kw: float, pv_kw: float, soc: float, grid_connected: bool, trust: dict[str, float] | None = None) -> float:
        net = load_kw - pv_kw
        trust = trust or {}
        soc_trust = trust.get("soc", 1.0)
        if soc_trust < 0.35:
            return 0.0
        if grid_connected:
            if net > self.config.grid_peak_threshold_kw and soc > self.config.reserve_soc:
                return min(self.config.max_battery_kw, net - self.config.grid_peak_threshold_kw)
            if net < 0 and soc < 0.9:
                return -min(self.config.max_battery_kw, -net)
            return 0.0
        if net > 0 and soc > self.config.reserve_soc:
            return min(self.config.max_battery_kw, net)
        if net < 0 and soc < 0.9:
            return -min(self.config.max_battery_kw, -net)
        return 0.0
