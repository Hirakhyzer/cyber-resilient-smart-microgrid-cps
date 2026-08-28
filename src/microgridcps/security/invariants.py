def power_balance_residual_kw(values: dict[str, float]) -> float:
    return values.get("pv_kw", 0.0) + values.get("battery_kw", 0.0) + values.get("grid_kw", 0.0) - values.get("load_kw", 0.0)

def physical_bound_scores(values: dict[str, float]) -> dict[str, float]:
    return {
        "soc": 2.0 if not (0.0 <= values.get("soc", 0.5) <= 1.0) else 0.0,
        "voltage_pu": max(0.0, abs(values.get("voltage_pu", 1.0) - 1.0) / 0.08 - 1.0),
        "frequency_hz": max(0.0, abs(values.get("frequency_hz", 50.0) - 50.0) / 0.8 - 1.0),
    }
