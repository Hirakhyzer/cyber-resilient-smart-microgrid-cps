from dataclasses import dataclass
from .invariants import physical_bound_scores
from .fusion import fuse_scores

@dataclass(frozen=True)
class DetectorConfig:
    soc_tolerance: float = 0.055
    voltage_tolerance_pu: float = 0.025
    frequency_tolerance_hz: float = 0.22
    power_balance_tolerance_kw: float = 4.0
    persistence_steps: int = 3

class HybridDetector:
    def __init__(self, config: DetectorConfig | None = None):
        self.config = config or DetectorConfig()
        self.persistence = 0

    def evaluate(self, measured: dict[str, float], predicted: dict[str, float], temporal_score: float, balance_residual_kw: float) -> tuple[float, bool, dict[str, float]]:
        src = {
            "soc": abs(measured["soc"] - predicted["soc"]) / self.config.soc_tolerance,
            "voltage_pu": abs(measured["voltage_pu"] - predicted["voltage_pu"]) / self.config.voltage_tolerance_pu,
            "frequency_hz": abs(measured["frequency_hz"] - predicted["frequency_hz"]) / self.config.frequency_tolerance_hz,
            "pv_kw": abs(balance_residual_kw) / self.config.power_balance_tolerance_kw,
            "load_kw": abs(balance_residual_kw) / self.config.power_balance_tolerance_kw,
        }
        bounds = physical_bound_scores(measured)
        for k, v in bounds.items():
            src[k] = max(src.get(k, 0.0), v)
        score = fuse_scores(temporal_score, *src.values())
        self.persistence = self.persistence + 1 if score >= 1.0 else 0
        return score, self.persistence >= self.config.persistence_steps, src
