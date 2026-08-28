from dataclasses import dataclass
from .telemetry import TelemetryPacket

@dataclass
class FreshnessResult:
    stale_sequence: bool
    stale_timestamp: bool
    age_s: float

class FreshnessMonitor:
    def __init__(self):
        self.last_seq: int | None = None
        self.last_timestamp: float | None = None

    def check(self, packet: TelemetryPacket, now_s: float) -> FreshnessResult:
        stale_seq = self.last_seq is not None and packet.seq <= self.last_seq
        stale_ts = self.last_timestamp is not None and packet.timestamp_s <= self.last_timestamp
        self.last_seq = packet.seq
        self.last_timestamp = packet.timestamp_s
        return FreshnessResult(stale_seq, stale_ts, max(0.0, now_s - packet.timestamp_s))
