from app.telemetry.signal_heatmap import classify_signal_strength, compute_signal_score


def test_compute_signal_score_bands():
    assert compute_signal_score(-75) >= 80
    assert 40 <= compute_signal_score(-95) <= 79
    assert compute_signal_score(-115) <= 39


def test_classify_signal_strength():
    assert classify_signal_strength(-80) == "strong"
    assert classify_signal_strength(-95) == "marginal"
    assert classify_signal_strength(-115) == "weak"
