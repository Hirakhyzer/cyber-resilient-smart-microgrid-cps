from dataclasses import dataclass
import numpy as np
from .telemetry import TelemetryPacket

@dataclass(frozen=True)
class NetworkConfig:
    loss_probability: float = 0.01
    latency_steps: int = 1
    jitter_steps: int = 1
    seed: int = 13

class NetworkChannel:
    def __init__(self, config: NetworkConfig | None = None):
        self.config = config or NetworkConfig()
        if not 0 <= self.config.loss_probability <= 1:
            raise ValueError("loss_probability must be in [0,1]")
        self.rng = np.random.default_rng(self.config.seed)
        self.queue: list[tuple[int, TelemetryPacket]] = []
        self.step_index = 0

    def send(self, packet: TelemetryPacket) -> bool:
        if self.rng.random() < self.config.loss_probability:
            return False
        jitter = int(self.rng.integers(0, self.config.jitter_steps + 1)) if self.config.jitter_steps else 0
        delivery = self.step_index + self.config.latency_steps + jitter
        self.queue.append((delivery, packet.clone()))
        return True

    def receive(self) -> list[TelemetryPacket]:
        ready = [p for due, p in self.queue if due <= self.step_index]
        self.queue = [(due, p) for due, p in self.queue if due > self.step_index]
        self.step_index += 1
        return ready
