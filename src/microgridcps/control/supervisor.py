from enum import IntEnum

class SupervisorState(IntEnum):
    NORMAL = 0
    WATCH = 1
    CYBER_ANOMALY = 2
    ISOLATE_SOURCE = 3
    DEGRADED_OPERATION = 4
    ISLANDED = 5
    RECOVERY = 6
    EMERGENCY = 7

STATE_NAMES = {s.value: s.name for s in SupervisorState}

class ResilienceSupervisor:
    def __init__(self):
        self.state = SupervisorState.NORMAL
        self.clear_count = 0

    def update(self, anomaly: bool, score: float, isolated_source: str | None, grid_connected: bool, unserved_kw: float) -> SupervisorState:
        if unserved_kw > 15.0 or score >= 3.5:
            self.state = SupervisorState.EMERGENCY
            self.clear_count = 0
        elif anomaly and isolated_source is not None:
            self.state = SupervisorState.ISOLATE_SOURCE
            self.clear_count = 0
        elif anomaly:
            self.state = SupervisorState.CYBER_ANOMALY
            self.clear_count = 0
        elif not grid_connected:
            self.state = SupervisorState.ISLANDED
            self.clear_count += 1
        elif score >= 0.7:
            self.state = SupervisorState.WATCH
            self.clear_count = 0
        else:
            self.clear_count += 1
            self.state = SupervisorState.RECOVERY if self.clear_count < 4 and self.state != SupervisorState.NORMAL else SupervisorState.NORMAL
        return self.state
