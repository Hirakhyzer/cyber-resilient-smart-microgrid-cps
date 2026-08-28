def fuse_scores(*scores: float, mode: str = "max") -> float:
    vals = [max(0.0, float(s)) for s in scores]
    if not vals:
        return 0.0
    if mode == "mean":
        return sum(vals) / len(vals)
    return max(vals)
