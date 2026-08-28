class TrustManager:
    def __init__(self, sources: tuple[str, ...] = ("soc", "pv_kw", "load_kw", "voltage_pu", "frequency_hz"), decay: float = 0.18, recovery: float = 0.03):
        self.decay = decay
        self.recovery = recovery
        self.scores = {s: 1.0 for s in sources}

    def update(self, source_scores: dict[str, float]) -> dict[str, float]:
        for src, trust in list(self.scores.items()):
            evidence = max(0.0, source_scores.get(src, 0.0))
            if evidence >= 1.0:
                trust -= self.decay * min(2.0, evidence)
            else:
                trust += self.recovery * (1.0 - trust)
            self.scores[src] = min(1.0, max(0.0, trust))
        return dict(self.scores)
