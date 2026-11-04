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



def minimum_service_fraction(served_kw, required_kw) -> float:
    """Worst instantaneous served-demand fraction over a trajectory."""
    served = np.asarray(served_kw, dtype=float)
    required = np.asarray(required_kw, dtype=float)
    if served.shape != required.shape:
        raise ValueError("served_kw and required_kw must have matching shapes")
    fractions = np.ones_like(required, dtype=float)
    positive = required > 1e-12
    fractions[positive] = np.clip(served[positive] / required[positive], 0.0, 1.0)
    return float(np.min(fractions)) if fractions.size else 1.0


def interval_service_resilience(served_kw, required_kw, start_step: int, end_step: int) -> float:
    """Aggregate service resilience over a declared experiment interval."""
    served = np.asarray(served_kw, dtype=float)
    required = np.asarray(required_kw, dtype=float)
    if served.shape != required.shape:
        raise ValueError("served_kw and required_kw must have matching shapes")
    if not 0 <= start_step <= end_step <= len(served):
        raise ValueError("invalid interval")
    return service_resilience(served[start_step:end_step], required[start_step:end_step])


def interval_unserved_energy_kwh(unserved_kw, dt_h: float, start_step: int, end_step: int) -> float:
    values = np.asarray(unserved_kw, dtype=float)
    if dt_h <= 0.0:
        raise ValueError("dt_h must be positive")
    if not 0 <= start_step <= end_step <= len(values):
        raise ValueError("invalid interval")
    return float(np.sum(np.maximum(0.0, values[start_step:end_step])) * dt_h)


def recovery_time_seconds(
    served_kw,
    required_kw,
    reconnect_step: int,
    dt_seconds: float,
    threshold: float = 0.99,
    hold_steps: int = 5,
) -> float | None:
    """Time after reconnection until service is sustainably restored.

    Recovery is declared when the served-demand fraction remains at or above the
    threshold for the requested number of consecutive samples. None means that
    recovery was not demonstrated inside the simulated horizon.
    """
    served = np.asarray(served_kw, dtype=float)
    required = np.asarray(required_kw, dtype=float)
    if served.shape != required.shape:
        raise ValueError("served_kw and required_kw must have matching shapes")
    if not 0 <= reconnect_step < len(served):
        return None
    if dt_seconds <= 0.0:
        raise ValueError("dt_seconds must be positive")
    if not 0.0 < threshold <= 1.0:
        raise ValueError("threshold must be in (0, 1]")
    if not isinstance(hold_steps, int) or hold_steps <= 0:
        raise ValueError("hold_steps must be a positive integer")

    fraction = np.ones_like(required, dtype=float)
    positive = required > 1e-12
    fraction[positive] = np.clip(served[positive] / required[positive], 0.0, 1.0)

    final_start = len(fraction) - hold_steps
    for step in range(reconnect_step, final_start + 1):
        if np.all(fraction[step : step + hold_steps] >= threshold):
            return float((step - reconnect_step) * dt_seconds)
    return None
