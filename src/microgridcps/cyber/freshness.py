from dataclasses import dataclass
import math
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


class ReorderingAwareFreshnessMonitor:
    """Freshness monitor that tolerates bounded network reordering.

    v0.1 semantics are preserved in FreshnessMonitor. v0.2 uses this monitor with
    a reordering window derived from configured network jitter. A packet is stale
    only when it falls behind the highest observed sequence/timestamp by more than
    the allowed window.
    """

    def __init__(self, reorder_window_steps: int = 0, step_seconds: float = 60.0):
        if not isinstance(reorder_window_steps, int) or reorder_window_steps < 0:
            raise ValueError("reorder_window_steps must be a non-negative integer")
        if not math.isfinite(step_seconds) or step_seconds <= 0.0:
            raise ValueError("step_seconds must be finite and positive")
        self.reorder_window_steps = reorder_window_steps
        self.step_seconds = step_seconds
        self.max_seq: int | None = None
        self.max_timestamp: float | None = None

    def check(self, packet: TelemetryPacket, now_s: float) -> FreshnessResult:
        seq_floor = None if self.max_seq is None else self.max_seq - self.reorder_window_steps
        time_floor = None if self.max_timestamp is None else self.max_timestamp - self.reorder_window_steps * self.step_seconds
        stale_seq = seq_floor is not None and packet.seq < seq_floor
        stale_ts = time_floor is not None and packet.timestamp_s < time_floor
        self.max_seq = packet.seq if self.max_seq is None else max(self.max_seq, packet.seq)
        self.max_timestamp = packet.timestamp_s if self.max_timestamp is None else max(self.max_timestamp, packet.timestamp_s)
        return FreshnessResult(stale_seq, stale_ts, max(0.0, now_s - packet.timestamp_s))
