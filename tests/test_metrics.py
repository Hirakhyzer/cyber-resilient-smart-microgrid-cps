from microgridcps.metrics.cyber import cyber_metrics
from microgridcps.metrics.resilience import (
    critical_load_resilience,
    interval_service_resilience,
    interval_unserved_energy_kwh,
    minimum_service_fraction,
    recovery_time_seconds,
    service_resilience,
)

def test_metrics():
    m=cyber_metrics([0,1,1,0],[0,1,0,1]); assert m["tp"]==1 and m["fp"]==1
    assert service_resilience([8,9],[10,10])==0.85


def test_critical_load_resilience_assumes_critical_first_service():
    assert critical_load_resilience([5.0, 5.0], [10.0, 10.0], critical_fraction=0.5) == 1.0
    assert critical_load_resilience([2.5, 2.5], [10.0, 10.0], critical_fraction=0.5) == 0.5



def test_operational_resilience_metrics():
    served = [10.0, 5.0, 8.0, 10.0, 10.0, 10.0]
    required = [10.0] * 6
    unserved = [0.0, 5.0, 2.0, 0.0, 0.0, 0.0]

    assert minimum_service_fraction(served, required) == 0.5
    assert interval_service_resilience(served, required, 1, 3) == 0.65
    assert interval_unserved_energy_kwh(unserved, 1.0, 1, 3) == 7.0
    assert recovery_time_seconds(served, required, reconnect_step=3, dt_seconds=60.0, hold_steps=3) == 0.0
