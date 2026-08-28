# Microgrid Model

The physical model is a reduced-order, single-bus microgrid intended for CPS-security experiments, not protection design or power-flow validation. It includes PV, BESS, time-varying load, grid import/export, and islanded operation.

Positive battery power means discharge. The BESS is modeled as an energy bucket with charge/discharge efficiency and SOC limits. Voltage and frequency are simplified dynamic indicators driven by power imbalance, with a stiffer response while grid-connected.

All default capacities, limits, gains, and thresholds are illustrative until calibrated against a documented test system.
