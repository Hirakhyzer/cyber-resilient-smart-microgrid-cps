# Reproducibility

## Preserved v0.1 baseline

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
python -m pytest -q
python scripts/run_demo.py --config configs/baseline.json --out results/demo
python scripts/run_benchmark.py
```

## v0.2 experiments

Run the full default multi-seed study:

```bash
python scripts/run_v02_experiments.py
```

Run the preserved v0.1 versus v0.2 shared-scenario comparison:

```bash
python scripts/run_v02_comparison.py
```

Run the compact CI protocol locally:

```bash
python scripts/run_v02_experiments.py --ci
python scripts/run_v02_comparison.py --steps 240
```

CI tests Python 3.10, 3.11, and 3.12. Python 3.12 additionally executes the preserved v0.1 benchmark, compact v0.2 multi-seed experiment suite, and v0.1/v0.2 comparison.

For a publication preserve the commit SHA, config/protocol, all seeds, Python and dependency versions, exact commands, summary JSON, generated traces/figures, detector thresholds, estimator settings, and any manually excluded runs. Separate synthetic traces from future measured datasets.

The two-seed CI protocol is a regression screen, not a publication-scale sample. Use the default five-seed v0.2 protocol or a separately preregistered larger protocol for research reporting.
