from microgridcps.cyber.trust import TrustManager

def test_repeated_evidence_reduces_trust():
    t=TrustManager(); start=t.scores["soc"]
    for _ in range(4): t.update({"soc":2.0})
    assert t.scores["soc"]<start
