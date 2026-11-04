# v0.2 Resilience-First Experimental Protocol

v0.2 treats the repository primarily as a **resilient smart microgrid CPS research platform**. Cyber manipulation remains one possible disturbance class, but it is not the organizing principle of this study.

## Research objective

Evaluate how well the reduced-order microgrid preserves useful energy service when operating conditions become difficult or uncertain, including:

- utility-grid loss and islanded operation;
- limited battery energy and reduced battery capacity;
- reduced PV availability and cloud transients;
- increased load demand;
- degraded telemetry communication;
- combined resource, communication, and islanding stress;
- post-islanding service restoration.

The main question is:

> How much energy service can the microgrid preserve, especially critical service, as available resources and observability degrade?

## Experimental families

The primary resilience suite is implemented in:

```bash
python scripts/run_resilience_experiments.py
```

The default study uses five deterministic seeds. The compact CI screen uses:

```bash
python scripts/run_resilience_experiments.py --ci
```

Current scenarios are:

1. grid-connected baseline;
2. short islanding;
3. medium islanding;
4. long islanding;
5. low-initial-SOC islanding;
6. reduced-battery-capacity islanding;
7. reduced-PV islanding;
8. cloudy islanding;
9. high-load islanding;
10. communication-degraded islanding;
11. combined operational stress.

The existing telemetry/cyber experiments are retained as a secondary robustness study and are not removed.

## Primary resilience metrics

The resilience study prioritizes:

- aggregate service resilience;
- critical-load resilience proxy;
- minimum instantaneous service fraction;
- total unserved energy;
- islanding-period service resilience;
- islanding-period unserved energy;
- recovery time after grid reconnection;
- minimum battery SOC;
- estimator uncertainty;
- communication-fault fraction;
- maximum voltage and frequency deviation.

Cyber precision/recall can still be reported in dedicated security experiments, but they are not the headline metrics of this resilience suite.

## Physical-resource sensitivity controls

The additive `ResourceStressConfig` provides transparent experiment controls for:

- initial battery SOC;
- battery-capacity scaling;
- PV-capacity scaling;
- critical-load fraction.

Defaults reproduce the existing reduced-order v0.2 plant assumptions. These controls are intentionally simple sensitivity parameters, not calibrated battery-aging or PV-degradation models.

## Interpretation

The current plant is a reduced-order, single-bus simulation. Critical-load resilience is still an accounting proxy that assumes served power is credited to critical demand first; it does not represent feeder-level switching or protection coordination.

A result should therefore be interpreted as a **comparative resilience experiment inside this simulator**, not as an operational reliability guarantee.

The strongest future extensions are:

- explicit controllable critical and flexible load classes;
- restoration policies after reconnection;
- reserve-aware energy management;
- battery degradation and availability models;
- forecast uncertainty and stochastic renewable profiles;
- higher-fidelity validation with a documented power-system test case.
