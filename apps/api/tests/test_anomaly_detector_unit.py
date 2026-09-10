from app.telemetry.anomaly_detector import TelemetryAnomalyDetector


def test_no_anomalies_for_normal_telemetry():
    detector = TelemetryAnomalyDetector()
    result = detector.evaluate(
        {"voltage": 12.0, "temperature": 35.0, "rssi": -80, "altitude": 100, "speed": 10},
        previous_metrics={"voltage": 12.2, "rssi": -78, "altitude": 102, "speed": 11},
    )
    assert result == []


def test_voltage_drop_anomaly():
    detector = TelemetryAnomalyDetector()
    result = detector.evaluate(
        {"voltage": 10.0},
        previous_metrics={"voltage": 12.0},
    )
    assert len(result) == 1
    assert result[0].anomaly_type == "voltage_drop"
    assert result[0].severity == "warning"
    assert "16.7" in result[0].message


def test_voltage_drop_critical():
    detector = TelemetryAnomalyDetector()
    result = detector.evaluate(
        {"voltage": 8.0},
        previous_metrics={"voltage": 12.0},
    )
    assert result[0].severity == "critical"


def test_battery_overheat_anomaly():
    detector = TelemetryAnomalyDetector()
    result = detector.evaluate({"temperature": 58.0})
    assert len(result) == 1
    assert result[0].anomaly_type == "battery_overheat"
    assert result[0].severity == "warning"


def test_signal_loss_rssi_drop():
    detector = TelemetryAnomalyDetector()
    result = detector.evaluate(
        {"rssi": -110},
        previous_metrics={"rssi": -85},
    )
    assert any(a.anomaly_type == "signal_loss" for a in result)


def test_signal_loss_ping_delay():
    detector = TelemetryAnomalyDetector()
    result = detector.evaluate({"ping_delay_ms": 6000})
    assert len(result) == 1
    assert result[0].anomaly_type == "signal_loss"


def test_altitude_deviation():
    detector = TelemetryAnomalyDetector()
    result = detector.evaluate(
        {"altitude": 200},
        previous_metrics={"altitude": 120},
    )
    assert len(result) == 1
    assert result[0].anomaly_type == "altitude_deviation"


def test_speed_deviation():
    detector = TelemetryAnomalyDetector()
    result = detector.evaluate(
        {"speed": 30},
        previous_metrics={"speed": 10},
    )
    assert len(result) == 1
    assert result[0].anomaly_type == "speed_deviation"
