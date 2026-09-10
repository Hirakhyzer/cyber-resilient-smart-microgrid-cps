from dataclasses import dataclass, replace
from typing import Dict

@dataclass
class TelemetryPacket:
    seq: int
    timestamp_s: float
    values: Dict[str, float]
    source: str = "microgrid_gateway"
    # Simulation-only ground-truth provenance. It is never consumed by the
    # detector or controller; it only keeps evaluation labels aligned with the
    # exact packet after network delay, jitter, cloning, replay, or loss.
    simulation_attack_label: bool = False

    def clone(self) -> "TelemetryPacket":
        return replace(self, values=dict(self.values))
