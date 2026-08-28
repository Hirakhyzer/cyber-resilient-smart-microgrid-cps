def trusted_command(request_kw: float, supervisor_state: int, max_abs_kw: float = 40.0) -> float:
    p = min(max_abs_kw, max(-max_abs_kw, request_kw))
    if supervisor_state in (2, 3, 7):
        return 0.0
    if supervisor_state == 4:
        return 0.5 * p
    return p
