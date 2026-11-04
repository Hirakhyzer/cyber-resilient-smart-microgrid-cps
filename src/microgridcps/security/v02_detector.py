from __future__ import annotations

from dataclasses import dataclass
import math

from .invariants import physical_bound_scores
from .fusion import fuse_scores
from ..twin.uncertainty import uncertainty_aware_score


@dataclass(frozen=True)
class V02DetectorConfig:
    soc_tolerance: float = 0.055
    voltage_tolerance_pu: float = 0.025
    frequency_tolerance_hz: float = 0.22
    pv_tolerance_kw: float = 4.0
    load_tolerance_kw: float = 4.0
    power_balance_tolerance_kw: float = 4.0
    persistence_observations: int = 3

    def __post_init__(self) -> None:
        vals = (
            self.soc_tolerance,
            self.voltage_tolerance_pu,
            self.frequency_tolerance_hz,
            self.pv_tolerance_kw,
            self.load_tolerance_kw,
            self.power_balance_tolerance_kw,
        )
        if not all(math.isfinite(v) and v > 0.0 for v in vals):
            raise ValueError("detector tolerances must be finite and positive")
        if not isinstance(self.persistence_observations, int) or self.persistence_observations < 1:
            raise ValueError("persistence_observations must be a positive integer")


class UncertaintyAwareHybridDetector:
    """v0.2 detector using uncertainty-aware residual and temporal evidence.

    This class is additive: the v0.1 HybridDetector remains unchanged. PV and
    load residuals are separated so source isolation is not forced to break a
    power-balance tie between those channels.
    """

    def __init__(self, config: V02DetectorConfig | None = None):
        self.config = config or V02DetectorConfig()
        self.persistence = 0

    def evaluate(
        self,
        measured: dict[str, float],
        predicted: dict[str, float],
        uncertainty: dict[str, float],
        temporal_score: float,
        balance_residual_kw: float,
        dynamics_scores: dict[str, float] | None = None,
    ) -> tuple[float, bool, dict[str, float]]:
        dynamics_scores = dynamics_scores or {}
        src = {
            "soc": uncertainty_aware_score(
                measured["soc"] - predicted["soc"],
                self.config.soc_tolerance,
                uncertainty.get("soc", 0.0),
            ),
            "voltage_pu": uncertainty_aware_score(
                measured["voltage_pu"] - predicted["voltage_pu"],
                self.config.voltage_tolerance_pu,
                uncertainty.get("voltage_pu", 0.0),
            ),
            "frequency_hz": uncertainty_aware_score(
                measured["frequency_hz"] - predicted["frequency_hz"],
                self.config.frequency_tolerance_hz,
                uncertainty.get("frequency_hz", 0.0),
            ),
            "pv_kw": abs(measured["pv_kw"] - predicted.get("pv_kw", measured["pv_kw"])) / self.config.pv_tolerance_kw,
            "load_kw": abs(measured["load_kw"] - predicted.get("load_kw", measured["load_kw"])) / self.config.load_tolerance_kw,
        }
        for key in ("pv_kw", "load_kw"):
            src[key] = max(src[key], max(0.0, float(dynamics_scores.get(key, 0.0))))
        bounds = physical_bound_scores(measured)
        for key, value in bounds.items():
            src[key] = max(src.get(key, 0.0), value)

        balance_score = abs(balance_residual_kw) / self.config.power_balance_tolerance_kw
        score = fuse_scores(temporal_score, balance_score, *src.values())
        self.persistence = self.persistence + 1 if score >= 1.0 else 0
        return score, self.persistence >= self.config.persistence_observations, src
