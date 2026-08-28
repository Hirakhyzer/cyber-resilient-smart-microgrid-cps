#!/usr/bin/env python3
import argparse,csv,json
from pathlib import Path
import matplotlib.pyplot as plt
from common import load_config
from microgridcps import run_simulation,summarize

p=argparse.ArgumentParser(); p.add_argument("--config",default="configs/baseline.json"); p.add_argument("--out",default="results/demo"); a=p.parse_args()
out=Path(a.out); out.mkdir(parents=True,exist_ok=True)
r=run_simulation(load_config(a.config)); s=summarize(r)
keys=[k for k,v in r.items() if hasattr(v,"__len__") and not isinstance(v,(str,bytes))]
with (out/"timeseries.csv").open("w",newline="") as f:
    w=csv.writer(f); w.writerow(keys); w.writerows(zip(*(r[k] for k in keys)))
(out/"summary.json").write_text(json.dumps(s,indent=2))
plt.figure(figsize=(9,4)); plt.plot(r["time_h"],r["load_kw"],label="Load"); plt.plot(r["time_h"],r["pv_kw"],label="PV"); plt.plot(r["time_h"],r["battery_kw"],label="Battery"); plt.xlabel("Hour"); plt.ylabel("kW"); plt.legend(); plt.tight_layout(); plt.savefig(out/"power_balance.png",dpi=160); plt.close()
plt.figure(figsize=(9,4)); plt.plot(r["time_h"],r["anomaly_score"],label="Anomaly score"); plt.plot(r["time_h"],r["trust_soc"],label="SOC trust"); plt.xlabel("Hour"); plt.legend(); plt.tight_layout(); plt.savefig(out/"cyber_resilience.png",dpi=160); plt.close()
print(json.dumps(s,indent=2))
