import pytest

from microgridcps.twin.estimator import EstimatorConfig, ExponentialStateEstimator, TelemetryStateEstimator
from microgridcps.twin.uncertainty import uncertainty_aware_score
from microgridcps.security.temporal_integrity import TemporalIntegrityMonitor


def test_estimator_uncertainty_grows_without_measurements_and_contracts_on_correction():
    est = TelemetryStateEstimator({"soc": 0.6})
    u0 = est.snapshot().uncertainty["soc"]
    est.predict({"soc": 0.59})
    u1 = est.snapshot().uncertainty["soc"]
    est.correct({"soc": 0.61})
    u2 = est.snapshot().uncertainty["soc"]
    assert u1 > u0
    assert u2 < u1


def test_estimator_rejects_invalid_gain():
    with pytest.raises(ValueError):
        EstimatorConfig(measurement_gain=0.0)
    with pytest.raises(ValueError):
        ExponentialStateEstimator(alpha=float("nan"))


def test_uncertainty_aware_score_decreases_as_state_uncertainty_grows():
    confident = uncertainty_aware_score(0.1, tolerance=0.05, state_uncertainty=0.0)
    uncertain = uncertainty_aware_score(0.1, tolerance=0.05, state_uncertainty=0.2)
    assert uncertain < confident


def test_temporal_integrity_detects_stagnation_against_changing_prediction():
    monitor = TemporalIntegrityMonitor(window=4, stagnation_epsilon=1e-3, mismatch_tolerance=0.02)
    result = None
    for observed, predicted in [(0.5, 0.50), (0.5, 0.52), (0.5, 0.54), (0.5, 0.56)]:
        result = monitor.update(observed, predicted)
    assert result is not None
    assert result.stagnation_score > 1.0


def test_temporal_integrity_does_not_flag_matching_change_as_stagnation():
    monitor = TemporalIntegrityMonitor(window=4, stagnation_epsilon=1e-3, mismatch_tolerance=0.02)
    result = None
    for observed, predicted in [(0.50, 0.50), (0.52, 0.52), (0.54, 0.54), (0.56, 0.56)]:
        result = monitor.update(observed, predicted)
    assert result is not None
    assert result.stagnation_score <= 1.1
    assert result.change_mismatch_score < 0.1
