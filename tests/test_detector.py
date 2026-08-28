from microgridcps.security.detector import HybridDetector

def test_persistent_soc_residual_triggers():
    d=HybridDetector(); m={"soc":0.3,"voltage_pu":1.0,"frequency_hz":50.0}; p={"soc":0.6,"voltage_pu":1.0,"frequency_hz":50.0}
    alarm=False
    for _ in range(3): _,alarm,_=d.evaluate(m,p,0.0,0.0)
    assert alarm

def test_small_residual_no_alarm():
    d=HybridDetector(); m={"soc":0.61,"voltage_pu":1.003,"frequency_hz":50.02}; p={"soc":0.60,"voltage_pu":1.0,"frequency_hz":50.0}
    for _ in range(5): score,alarm,_=d.evaluate(m,p,0.0,0.2)
    assert not alarm and score<1.0
