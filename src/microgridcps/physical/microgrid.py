from dataclasses import dataclass
from .battery import BatteryModel, BatteryParams
from .grid import GridConnection, GridParams
from .loads import LoadModel, LoadParams
from .pv import PVModel, PVParams

@dataclass(frozen=True)
class MicrogridParams:
    nominal_frequency_hz: float = 50.0
    nominal_voltage_pu: float = 1.0
    frequency_gain: float = 0.018
    voltage_gain: float = 0.0025
    dynamic_relaxation: float = 0.35

@dataclass
class MicrogridState:
    battery_soc: float
    frequency_hz: float
    voltage_pu: float
    grid_connected: bool
    grid_power_kw: float = 0.0
    pv_power_kw: float = 0.0
    battery_power_kw: float = 0.0
    load_power_kw: float = 0.0
    served_load_kw: float = 0.0
    curtailed_pv_kw: float = 0.0
    unserved_load_kw: float = 0.0

class MicrogridModel:
    """Single-bus reduced-order microgrid research plant; not a protection/power-flow model."""
    def __init__(self, microgrid_params: MicrogridParams | None = None, battery_params: BatteryParams | None = None, grid_params: GridParams | None = None, pv_params: PVParams | None = None, load_params: LoadParams | None = None):
        self.params = microgrid_params or MicrogridParams()
        self.battery = BatteryModel(battery_params)
        self.grid = GridConnection(grid_params)
        self.pv = PVModel(pv_params)
        self.loads = LoadModel(load_params)
        self.frequency_hz = self.params.nominal_frequency_hz
        self.voltage_pu = self.params.nominal_voltage_pu

    def step(self, hour: float, battery_request_kw: float, dt_h: float, cloud_factor: float = 1.0, load_scale: float = 1.0, grid_connected: bool = True) -> MicrogridState:
        self.grid.set_connected(grid_connected)
        pv_available = self.pv.available_power_kw(hour, cloud_factor)
        load = self.loads.demand_kw(hour, load_scale)
        battery_p = self.battery.step(battery_request_kw, dt_h)
        net_demand = load - pv_available - battery_p
        grid_p = self.grid.exchange_kw(net_demand)
        balance = pv_available + battery_p + grid_p - load

        if grid_connected:
            target_f = self.params.nominal_frequency_hz + 0.002 * balance
            target_v = self.params.nominal_voltage_pu + 0.0003 * balance
        else:
            target_f = self.params.nominal_frequency_hz + self.params.frequency_gain * balance
            target_v = self.params.nominal_voltage_pu + self.params.voltage_gain * balance

        a = self.params.dynamic_relaxation
        self.frequency_hz += a * (target_f - self.frequency_hz)
        self.voltage_pu += a * (target_v - self.voltage_pu)

        if balance >= 0:
            served = load
            unserved = 0.0
            curtailed = max(0.0, balance)
        else:
            unserved = min(load, -balance) if not grid_connected else 0.0
            served = max(0.0, load - unserved)
            curtailed = 0.0

        return MicrogridState(
            battery_soc=self.battery.soc, frequency_hz=self.frequency_hz, voltage_pu=self.voltage_pu,
            grid_connected=grid_connected, grid_power_kw=grid_p, pv_power_kw=pv_available, battery_power_kw=battery_p,
            load_power_kw=load, served_load_kw=served, curtailed_pv_kw=curtailed, unserved_load_kw=unserved,
        )
