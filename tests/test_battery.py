from microgridcps.physical.battery import BatteryModel

def test_discharge_reduces_soc():
    b=BatteryModel(); s=b.soc; p=b.step(20,0.25); assert p>0 and b.soc<s

def test_charge_increases_soc():
    b=BatteryModel(); s=b.soc; p=b.step(-20,0.25); assert p<0 and b.soc>s
