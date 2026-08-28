from microgridcps.cyber.network import NetworkChannel,NetworkConfig
from microgridcps.cyber.telemetry import TelemetryPacket

def test_zero_loss_delivery():
    n=NetworkChannel(NetworkConfig(0.0,1,0,1)); n.send(TelemetryPacket(1,0,{"x":1.0})); assert n.receive()==[]; assert len(n.receive())==1
