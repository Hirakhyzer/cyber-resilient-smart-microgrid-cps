from microgridcps.metrics.cyber import cyber_metrics
from microgridcps.metrics.resilience import service_resilience

def test_metrics():
    m=cyber_metrics([0,1,1,0],[0,1,0,1]); assert m["tp"]==1 and m["fp"]==1
    assert service_resilience([8,9],[10,10])==0.85
