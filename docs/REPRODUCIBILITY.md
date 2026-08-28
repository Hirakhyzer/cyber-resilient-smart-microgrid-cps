# Reproducibility

Recommended baseline:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
pytest
python scripts/run_demo.py --config configs/baseline.json --out results/demo
python scripts/run_benchmark.py
```

For a publication preserve the commit SHA, config JSON, seed, environment/package list, exact command, summary JSON, timeseries CSV, and generated figures. Separate synthetic traces from any future measured datasets.
