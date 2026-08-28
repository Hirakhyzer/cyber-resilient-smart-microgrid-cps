# Architecture

The simulator is organized as a closed cyber-physical loop with seven research layers: physical DER plant, sensing/telemetry, communication, digital twin, hybrid detection/trust, resilience supervision, and energy management/control.

The current v0.1 is intentionally middleware-independent. Future adapters may connect the same interfaces to pandapower, OpenDSS, PyPSA, FMI/FMU, or HIL environments while keeping cyber experiments isolated.

Key design principle: a cyber alert should be connected to a measurable physical consequence or inconsistency rather than treated as an isolated network event.
