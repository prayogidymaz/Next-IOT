"""Deterministic mock weather & wind vector field generator."""

from __future__ import annotations

import math
from hashlib import sha1

from app.telemetry.schemas import WeatherVectorPoint, WeatherVectorResponse
from app.telemetry.weather_safety import evaluate_flight_safety

METERS_PER_DEG_LAT = 111_320.0


def _seed_value(lat: float, lon: float, salt: str) -> float:
    digest = sha1(f"{lat:.5f}:{lon:.5f}:{salt}".encode()).hexdigest()
    return int(digest[:8], 16) / 0xFFFFFFFF


def _offset_meters(lat: float, lon: float, north_m: float, east_m: float) -> tuple[float, float]:
    dlat = north_m / METERS_PER_DEG_LAT
    cos_lat = math.cos(math.radians(lat))
    dlon = east_m / (METERS_PER_DEG_LAT * cos_lat) if cos_lat else 0.0
    return lat + dlat, lon + dlon


def generate_weather_at(lat: float, lon: float) -> dict[str, float]:
    """Generate mock weather scalars for a coordinate."""
    base = _seed_value(lat, lon, "weather")
    wind_speed = round(4.0 + base * 14.0, 2)
    wind_direction_deg = round(base * 360.0, 1)
    visibility_m = round(8000 - base * 5000, 0)
    rain_rate = round(max(0.0, (base - 0.65) * 18.0), 2)
    return {
        "wind_speed_m_s": wind_speed,
        "wind_direction_deg": wind_direction_deg,
        "visibility_m": visibility_m,
        "rain_rate_mm_h": rain_rate,
    }


def generate_weather_vector_field(
    *,
    lat: float,
    lon: float,
    radius_m: float,
) -> WeatherVectorResponse:
    radius_m = max(100.0, min(radius_m, 20_000.0))
    center = generate_weather_at(lat, lon)
    safety = evaluate_flight_safety(
        wind_speed_m_s=center["wind_speed_m_s"],
        rain_rate_mm_h=center["rain_rate_mm_h"],
    )

    spacing = max(250.0, radius_m / 4.0)
    steps = max(1, int(radius_m / spacing))
    vectors: list[WeatherVectorPoint] = []

    for i in range(-steps, steps + 1):
        for j in range(-steps, steps + 1):
            north = i * spacing
            east = j * spacing
            if math.hypot(north, east) > radius_m:
                continue
            point_lat, point_lon = _offset_meters(lat, lon, north, east)
            sample = generate_weather_at(point_lat, point_lon)
            vectors.append(
                WeatherVectorPoint(
                    lat=round(point_lat, 7),
                    lon=round(point_lon, 7),
                    wind_speed_m_s=sample["wind_speed_m_s"],
                    wind_direction_deg=sample["wind_direction_deg"],
                )
            )

    return WeatherVectorResponse(
        lat=lat,
        lon=lon,
        radius_m=radius_m,
        wind_speed_m_s=center["wind_speed_m_s"],
        wind_direction_deg=center["wind_direction_deg"],
        visibility_m=center["visibility_m"],
        rain_rate_mm_h=center["rain_rate_mm_h"],
        flight_safety_status=safety.value,
        vector_count=len(vectors),
        vectors=vectors,
    )


def weather_metrics_for_telemetry(lat: float, lon: float) -> dict[str, float]:
    """Compact weather metrics for drone simulator telemetry payloads."""
    sample = generate_weather_at(lat, lon)
    safety = evaluate_flight_safety(
        wind_speed_m_s=sample["wind_speed_m_s"],
        rain_rate_mm_h=sample["rain_rate_mm_h"],
    )
    return {
        "wind_speed_m_s": sample["wind_speed_m_s"],
        "wind_direction_deg": sample["wind_direction_deg"],
        "visibility_m": sample["visibility_m"],
        "rain_rate_mm_h": sample["rain_rate_mm_h"],
        "flight_safety_status_code": {"SAFE": 0, "CAUTION": 1, "NO_FLY": 2}[safety.value],
    }
