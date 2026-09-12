import pytest
from httpx import AsyncClient

from tests.test_commands import _register_and_create_device


@pytest.mark.asyncio
async def test_weather_vector_endpoint(client: AsyncClient, unique_slug: str, unique_email: str):
    ctx = await _register_and_create_device(client, unique_slug, unique_email)

    resp = await client.get(
        "/api/v1/telemetry/weather-vector",
        headers={"Authorization": f"Bearer {ctx['token']}"},
        params={"lat": -6.2088, "lon": 106.8456, "radius": 1500},
    )
    assert resp.status_code == 200
    body = resp.json()
    assert body["flight_safety_status"] in {"SAFE", "CAUTION", "NO_FLY"}
    assert body["vector_count"] == len(body["vectors"])
    assert body["vectors"]
    assert "wind_speed_m_s" in body
    assert "wind_direction_deg" in body


@pytest.mark.asyncio
async def test_weather_vector_validation(client: AsyncClient, unique_slug: str, unique_email: str):
    ctx = await _register_and_create_device(client, unique_slug, unique_email)

    resp = await client.get(
        "/api/v1/telemetry/weather-vector",
        headers={"Authorization": f"Bearer {ctx['token']}"},
        params={"lat": 95, "lon": 106.8456, "radius": 1000},
    )
    assert resp.status_code == 422
