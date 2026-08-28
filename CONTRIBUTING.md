# Contributing

Contributions are welcome when they improve modeling clarity, reproducibility, defensive cybersecurity experiments, metrics, tests, or documentation.

Before a pull request: run `pytest`, run affected benchmark scripts, document units and parameter provenance, preserve deterministic seeds, label synthetic data, and add tests for changed behavior.

Cybersecurity additions must remain simulator-only and defensive. Avoid protocol-specific exploit payloads, credentials, device targeting, or instructions for interacting with operational infrastructure.
