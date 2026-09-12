from app.telemetry.weather_generator import generate_weather_at, generate_weather_vector_field
from app.telemetry.weather_safety import FlightSafetyStatus, evaluate_flight_safety


def test_generate_weather_at_is_deterministic():
    first = generate_weather_at(-6.2088, 106.8456)
    second = generate_weather_at(-6.2088, 106.8456)
    assert first == second
    assert first["wind_speed_m_s"] >= 4.0


def test_generate_weather_vector_field_contains_vectors():
    field = generate_weather_vector_field(lat=-6.2088, lon=106.8456, radius_m=1000)
    assert field.vector_count == len(field.vectors)
    assert field.vector_count >= 1
    assert field.flight_safety_status in {
        FlightSafetyStatus.SAFE.value,
        FlightSafetyStatus.CAUTION.value,
        FlightSafetyStatus.NO_FLY.value,
    }
    assert field.flight_safety_status == evaluate_flight_safety(
        wind_speed_m_s=field.wind_speed_m_s,
        rain_rate_mm_h=field.rain_rate_mm_h,
    ).value
