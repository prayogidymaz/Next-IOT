"""Weather vector API service."""

from __future__ import annotations

from fastapi import HTTPException, status

from app.telemetry.schemas import WeatherVectorResponse
from app.telemetry.weather_generator import generate_weather_vector_field


async def get_weather_vector(
    *,
    lat: float,
    lon: float,
    radius_m: float = 2000.0,
) -> WeatherVectorResponse:
    if lat < -90 or lat > 90:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="lat must be between -90 and 90")
    if lon < -180 or lon > 180:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="lon must be between -180 and 180")
    if radius_m <= 0:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="radius must be positive")

    return generate_weather_vector_field(lat=lat, lon=lon, radius_m=radius_m)
