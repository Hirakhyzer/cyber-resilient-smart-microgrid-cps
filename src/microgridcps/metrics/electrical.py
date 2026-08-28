import numpy as np

def electrical_metrics(result):
    f=np.asarray(result["frequency_hz"]); v=np.asarray(result["voltage_pu"]); soc=np.asarray(result["soc_true"]); un=np.asarray(result["unserved_kw"])
    return {"max_frequency_deviation_hz": float(np.max(np.abs(f-50.0))), "max_voltage_deviation_pu": float(np.max(np.abs(v-1.0))), "min_soc": float(np.min(soc)), "unserved_energy_kwh": float(np.sum(un) * result["dt_h"])}
