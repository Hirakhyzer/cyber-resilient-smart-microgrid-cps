from microgridcps.cyber.attacks import AttackConfig,apply_attack
from microgridcps.cyber.telemetry import TelemetryPacket

def test_soc_bias_only_in_window():
    p=TelemetryPacket(1,0,{"soc":0.5,"pv_kw":0,"load_kw":0,"voltage_pu":1,"frequency_hz":50})
    c=AttackConfig(2,4,soc_bias=0.2)
    assert apply_attack(p,1,c).values["soc"]==0.5
    assert abs(apply_attack(p,2,c).values["soc"]-0.7)<1e-9

def test_replay_preserves_old_metadata_by_default():
    p=TelemetryPacket(10,100,{"soc":0.5}); old=TelemetryPacket(2,20,{"soc":0.6}); c=AttackConfig(0,20,replay=True)
    out=apply_attack(p,10,c,replay_snapshot=old); assert out.seq==2 and out.timestamp_s==20
