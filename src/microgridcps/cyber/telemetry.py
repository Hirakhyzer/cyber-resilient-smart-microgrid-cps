from dataclasses import dataclass, replace
from typing import Dict

@dataclass
class TelemetryPacket:
    seq: int
    timestamp_s: float
    values: Dict[str, float]
    source: str = "microgrid_gateway"

    def clone(self) -> "TelemetryPacket":
        return replace(self, values=dict(self.values))
