from microgridcps.metrics.cyber import cyber_metrics
from microgridcps.metrics.resilience import critical_load_resilience, service_resilience

def test_metrics():
    m=cyber_metrics([0,1,1,0],[0,1,0,1]); assert m["tp"]==1 and m["fp"]==1
    assert service_resilience([8,9],[10,10])==0.85


def test_critical_load_resilience_assumes_critical_first_service():
    assert critical_load_resilience([5.0, 5.0], [10.0, 10.0], critical_fraction=0.5) == 1.0
    assert critical_load_resilience([2.5, 2.5], [10.0, 10.0], critical_fraction=0.5) == 0.5
