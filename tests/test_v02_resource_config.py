import pytest

from microgridcps.v02 import ResourceStressConfig


def test_resource_configuration_defaults_are_valid():
    config = ResourceStressConfig()
    assert config.initial_soc == 0.65
    assert config.battery_capacity_scale == 1.0
    assert config.pv_capacity_scale == 1.0
    assert config.critical_fraction == 0.55


def test_resource_configuration_rejects_invalid_values():
    with pytest.raises(ValueError):
        ResourceStressConfig(initial_soc=0.15)
    with pytest.raises(ValueError):
        ResourceStressConfig(battery_capacity_scale=0.0)
    with pytest.raises(ValueError):
        ResourceStressConfig(pv_capacity_scale=-1.0)
