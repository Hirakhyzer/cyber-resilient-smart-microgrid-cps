import numpy as np

from microgridcps.cyber.attacks import AttackConfig
from microgridcps.cyber.network import NetworkConfig
from microgridcps.security.v02_detector import UncertaintyAwareHybridDetector
from microgridcps.v02 import PhysicalDisturbanceConfig, V02SimulationConfig, run_v02_simulation, summarize_v02


def test_v02_total_loss_does_not_expose_hidden_measurements():
    result = run_v02_simulation(
        V02SimulationConfig(
            steps=30,
            network=NetworkConfig(loss_probability=1.0, latency_steps=0, jitter_steps=0, seed=5),
        )
    )
    summary = summarize_v02(result)
    assert summary["communication_fault_fraction"] == 1.0
    assert summary["packet_delivery_fraction"] == 0.0
    assert np.isnan(result["soc_measured"]).all()
    assert result["soc_control"][0] != result["soc_true"][0]


def test_v02_attack_labels_follow_delivered_packets_under_latency():
    result = run_v02_simulation(
        V02SimulationConfig(
            steps=140,
            network=NetworkConfig(loss_probability=0.0, latency_steps=2, jitter_steps=1, seed=6),
            attack=AttackConfig(40, 70, soc_bias=-0.2),
        )
    )
    summary = summarize_v02(result)
    assert summary["attack_packets_generated"] == 30
    assert summary["attack_packets_dropped"] == 0
    assert summary["attack_packets_observed"] == 30
    assert len(result["detection_labels"]) == summary["packets_delivered"]


def test_v02_legitimate_disturbance_is_not_labeled_as_attack_truth():
    result = run_v02_simulation(
        V02SimulationConfig(
            steps=100,
            disturbance=PhysicalDisturbanceConfig(30, 60, cloud_factor=0.5, load_scale=1.15),
        )
    )
    summary = summarize_v02(result)
    assert summary["attack_packets_generated"] == 0
    assert int(result["disturbance_active"].sum()) == 30
    assert summary["disturbance_alarm_fraction"] >= 0.0


def test_v02_detector_separates_load_and_pv_evidence():
    detector = UncertaintyAwareHybridDetector()
    measured = {"soc": 0.6, "voltage_pu": 1.0, "frequency_hz": 50.0, "pv_kw": 20.0, "load_kw": 60.0}
    predicted = {"soc": 0.6, "voltage_pu": 1.0, "frequency_hz": 50.0, "pv_kw": 20.0, "load_kw": 40.0}
    _, _, scores = detector.evaluate(measured, predicted, {}, 0.0, balance_residual_kw=-20.0)
    assert scores["load_kw"] > scores["pv_kw"]
