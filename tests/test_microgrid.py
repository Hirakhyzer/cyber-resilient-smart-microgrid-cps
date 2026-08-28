from microgridcps.physical.microgrid import MicrogridModel

def test_grid_connected_state_finite():
    m=MicrogridModel(); s=m.step(12.0,0.0,1/60,grid_connected=True)
    assert 0<s.voltage_pu<2 and 40<s.frequency_hz<60

def test_islanded_deficit_can_create_unserved_load():
    m=MicrogridModel(); m.battery.soc=m.battery.params.min_soc
    s=m.step(20.0,0.0,1/60,cloud_factor=0.0,load_scale=2.0,grid_connected=False)
    assert s.unserved_load_kw>0
