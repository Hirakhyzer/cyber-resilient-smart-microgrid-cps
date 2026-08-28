import numpy as np

def service_resilience(served_kw, required_kw) -> float:
    s=np.asarray(served_kw, dtype=float); r=np.asarray(required_kw, dtype=float)
    denom=float(np.sum(r))
    return 1.0 if denom <= 1e-12 else max(0.0, min(1.0, float(np.sum(s)/denom)))
