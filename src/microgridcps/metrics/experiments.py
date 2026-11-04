from __future__ import annotations

from collections import Counter
import numpy as np


def detection_delay_seconds(attack_active, alarms, dt_seconds: float) -> float | None:
    attack = np.asarray(attack_active, dtype=bool)
    alarm = np.asarray(alarms, dtype=bool)
    if attack.size != alarm.size:
        raise ValueError("attack_active and alarms must have equal length")
    starts = np.flatnonzero(attack)
    if starts.size == 0:
        return None
    first_attack = int(starts[0])
    candidates = np.flatnonzero(alarm & (np.arange(alarm.size) >= first_attack))
    if candidates.size == 0:
        return None
    return float((int(candidates[0]) - first_attack) * dt_seconds)


def supervisor_occupancy(states) -> dict[str, float]:
    values = [int(v) for v in states]
    if not values:
        return {}
    counts = Counter(values)
    n = len(values)
    return {str(state): count / n for state, count in sorted(counts.items())}
