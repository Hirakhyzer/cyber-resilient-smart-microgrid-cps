def isolate_source(source_scores: dict[str, float], threshold: float = 1.0) -> str | None:
    if not source_scores:
        return None
    source, score = max(source_scores.items(), key=lambda kv: kv[1])
    return source if score >= threshold else None
