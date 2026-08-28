from dataclasses import dataclass, field

@dataclass
class BaseAgent:
    name: str
    trust: float = 1.0
    state: dict[str, float] = field(default_factory=dict)

    def observe(self, **values: float) -> None:
        self.state.update(values)
