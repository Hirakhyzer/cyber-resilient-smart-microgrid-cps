import numpy as np


def service_resilience(served_kw, required_kw) -> float:
    s = np.asarray(served_kw, dtype=float)
    r = np.asarray(required_kw, dtype=float)
    denom = float(np.sum(r))
    return 1.0 if denom <= 1e-12 else max(0.0, min(1.0, float(np.sum(s) / denom)))


def critical_load_resilience(served_kw, required_kw, critical_fraction: float = 0.55) -> float:
    """Critical-load service proxy assuming critical-first allocation.

    The reduced-order plant does not model individual feeder shedding. This metric
    therefore makes the allocation assumption explicit: aggregate served power is
    credited to critical demand first, then to non-critical demand. It is an
    accounting proxy for experiments, not evidence of a protection scheme.
    """
    if not 0.0 < critical_fraction <= 1.0:
        raise ValueError("critical_fraction must be in (0, 1]")
    served = np.asarray(served_kw, dtype=float)
    required = np.asarray(required_kw, dtype=float)
    if served.shape != required.shape:
        raise ValueError("served_kw and required_kw must have matching shapes")
    critical_required = np.maximum(0.0, required) * critical_fraction
    critical_served = np.minimum(np.maximum(0.0, served), critical_required)
    denom = float(np.sum(critical_required))
    return 1.0 if denom <= 1e-12 else max(0.0, min(1.0, float(np.sum(critical_served) / denom)))
