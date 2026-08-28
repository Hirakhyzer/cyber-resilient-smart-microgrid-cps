from dataclasses import dataclass

@dataclass(frozen=True)
class GridParams:
    import_limit_kw: float = 120.0
    export_limit_kw: float = 80.0

class GridConnection:
    """Simplified point of common coupling. Positive exchange imports power."""
    def __init__(self, params: GridParams | None = None):
        self.params = params or GridParams()
        self.connected = True

    def set_connected(self, connected: bool) -> None:
        self.connected = bool(connected)

    def exchange_kw(self, net_demand_kw: float) -> float:
        if not self.connected:
            return 0.0
        return min(self.params.import_limit_kw, max(-self.params.export_limit_kw, net_demand_kw))
