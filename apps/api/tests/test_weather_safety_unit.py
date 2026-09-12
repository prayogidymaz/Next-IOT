import pytest

from app.telemetry.weather_safety import FlightSafetyStatus, evaluate_flight_safety


@pytest.mark.parametrize(
    ("wind", "rain", "expected"),
    [
        (5.0, 0.0, FlightSafetyStatus.SAFE),
        (10.0, 0.0, FlightSafetyStatus.CAUTION),
        (12.5, 2.0, FlightSafetyStatus.CAUTION),
        (15.1, 0.0, FlightSafetyStatus.NO_FLY),
        (8.0, 10.1, FlightSafetyStatus.NO_FLY),
        (20.0, 15.0, FlightSafetyStatus.NO_FLY),
    ],
)
def test_evaluate_flight_safety(wind, rain, expected):
    assert evaluate_flight_safety(wind_speed_m_s=wind, rain_rate_mm_h=rain) == expected
