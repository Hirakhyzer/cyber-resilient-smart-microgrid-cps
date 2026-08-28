from dataclasses import dataclass
from .telemetry import TelemetryPacket

@dataclass(frozen=True)
class AttackConfig:
    start_step: int = 180
    end_step: int = 300
    soc_bias: float = 0.0
    pv_bias_kw: float = 0.0
    load_bias_kw: float = 0.0
    voltage_bias_pu: float = 0.0
    frequency_bias_hz: float = 0.0
    replay: bool = False
    freeze: bool = False
    rewrite_replay_metadata: bool = False

def apply_attack(packet: TelemetryPacket, step: int, cfg: AttackConfig, replay_snapshot: TelemetryPacket | None = None, freeze_snapshot: TelemetryPacket | None = None) -> TelemetryPacket:
    """Synthetic in-memory fault/attack effects for defensive experiments only."""
    active = cfg.start_step <= step < cfg.end_step
    if not active:
        return packet.clone()
    if cfg.replay and replay_snapshot is not None:
        out = replay_snapshot.clone()
        if cfg.rewrite_replay_metadata:
            out.seq, out.timestamp_s = packet.seq, packet.timestamp_s
        return out
    if cfg.freeze and freeze_snapshot is not None:
        out = freeze_snapshot.clone()
        out.seq, out.timestamp_s = packet.seq, packet.timestamp_s
        return out
    out = packet.clone()
    out.values["soc"] += cfg.soc_bias
    out.values["pv_kw"] += cfg.pv_bias_kw
    out.values["load_kw"] += cfg.load_bias_kw
    out.values["voltage_pu"] += cfg.voltage_bias_pu
    out.values["frequency_hz"] += cfg.frequency_bias_hz
    return out
