def temporal_score(stale_sequence: bool, stale_timestamp: bool, age_s: float, max_age_s: float) -> float:
    score = 0.0
    if stale_sequence or stale_timestamp:
        score = max(score, 2.0)
    if max_age_s > 0:
        score = max(score, age_s / max_age_s)
    return score
