import uuid
from datetime import UTC, datetime

from app.models.telemetry_reading import TelemetryReading
from app.telemetry.analytics import _aggregate_readings, _compute_total_distance_m
from app.telemetry.export_generator import generate_csv, generate_json_export, generate_kml, render_export


def _reading(metrics: dict, *, offset_minutes: int = 0) -> TelemetryReading:
    ts = datetime(2026, 9, 12, 10, offset_minutes, tzinfo=UTC)
    return TelemetryReading(
        id=uuid.uuid4(),
        device_id=uuid.uuid4(),
        tenant_id=uuid.uuid4(),
        recorded_at=ts,
        metrics=metrics,
    )


def test_generate_csv_includes_gps_and_metrics():
    readings = [
        _reading({"latitude": -6.2, "longitude": 106.8, "speed": 12.5, "voltage": 11.8}),
        _reading({"latitude": -6.201, "longitude": 106.801, "speed": 15.0, "voltage": 11.5}, offset_minutes=1),
    ]
    csv_text = generate_csv(readings)
    assert "reading_id,recorded_at" in csv_text
    assert "-6.2" in csv_text
    assert "12.5" in csv_text
    assert "11.5" in csv_text


def test_generate_kml_contains_coordinates_and_flight_path():
    device_id = uuid.uuid4()
    readings = [
        _reading({"latitude": -6.2, "longitude": 106.8, "altitude": 50}),
        _reading({"latitude": -6.201, "longitude": 106.801, "altitude": 55}, offset_minutes=1),
    ]
    kml = generate_kml(readings, device_id=device_id, hours=24)
    assert "<?xml" in kml
    assert "106.8000000,-6.2000000" in kml
    assert "Flight Path" in kml
    assert "LineString" in kml


def test_render_export_json_filename():
    device_id = uuid.uuid4()
    readings = [_reading({"temperature": 25.0})]
    content, media_type, filename = render_export(
        readings,
        device_id=device_id,
        hours=1,
        export_format="json",
    )
    assert media_type == "application/json"
    assert filename.endswith(".json")
    assert str(device_id) in content


def test_aggregate_readings_computes_stats():
    readings = [
        _reading({"speed": 10.0, "altitude": 40.0, "voltage": 12.0}),
        _reading({"speed": 20.0, "altitude": 60.0, "voltage": 11.2}, offset_minutes=1),
    ]
    stats = _aggregate_readings(readings)
    assert stats["max_speed_m_s"] == 20.0
    assert stats["avg_altitude_m"] == 50.0
    assert stats["min_voltage_v"] == 11.2


def test_compute_total_distance_m_from_gps_track():
    readings = [
        _reading({"latitude": -6.2, "longitude": 106.8}),
        _reading({"latitude": -6.201, "longitude": 106.801}, offset_minutes=1),
    ]
    distance = _compute_total_distance_m(readings)
    assert distance > 0
