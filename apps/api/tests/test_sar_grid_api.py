import pytest
from httpx import AsyncClient

from tests.test_commands import PASSWORD, _register_and_create_device


@pytest.mark.asyncio
async def test_sar_grid_endpoint_expanding_square(client: AsyncClient, unique_slug: str, unique_email: str):
    ctx = await _register_and_create_device(client, unique_slug, unique_email)

    resp = await client.post(
        "/api/v1/mission/sar-grid",
        headers={"Authorization": f"Bearer {ctx['token']}"},
        json={
            "lkp_lat": -6.2088,
            "lkp_lon": 106.8456,
            "radius_m": 500,
            "pattern": "expanding_square",
            "leg_spacing_m": 100,
        },
    )
    assert resp.status_code == 200
    body = resp.json()
    assert body["pattern"] == "expanding_square"
    assert body["waypoint_count"] >= 2
    assert body["waypoints"][0]["label"] == "LKP"
    assert len(body["tracks"]) >= 1


@pytest.mark.asyncio
async def test_sar_grid_endpoint_parallel_track(client: AsyncClient, unique_slug: str, unique_email: str):
    ctx = await _register_and_create_device(client, unique_slug, unique_email)

    resp = await client.post(
        "/api/v1/mission/sar-grid",
        headers={"Authorization": f"Bearer {ctx['token']}"},
        json={
            "lkp_lat": -6.2088,
            "lkp_lon": 106.8456,
            "radius_m": 300,
            "pattern": "parallel_track",
        },
    )
    assert resp.status_code == 200
    assert resp.json()["pattern"] == "parallel_track"


@pytest.mark.asyncio
async def test_dispatch_fail_safe_return_to_home(client: AsyncClient, unique_slug: str, unique_email: str):
    ctx = await _register_and_create_device(client, unique_slug, unique_email)

    resp = await client.post(
        f"/api/v1/devices/{ctx['device_id']}/commands",
        headers={"Authorization": f"Bearer {ctx['token']}"},
        json={
            "command_type": "RETURN_TO_HOME",
            "params": {"priority": "critical", "fail_safe": True, "reason": "Manual test"},
        },
    )
    assert resp.status_code == 201
    body = resp.json()
    assert body["command_type"] == "RETURN_TO_HOME"
    assert body["params"]["priority"] == "critical"


@pytest.mark.asyncio
async def test_dispatch_fail_safe_emergency_land(client: AsyncClient, unique_slug: str, unique_email: str):
    ctx = await _register_and_create_device(client, unique_slug, unique_email)

    resp = await client.post(
        f"/api/v1/devices/{ctx['device_id']}/commands",
        headers={"Authorization": f"Bearer {ctx['token']}"},
        json={
            "command_type": "EMERGENCY_LAND",
            "params": {"priority": "critical", "fail_safe": True, "reason": "Manual test"},
        },
    )
    assert resp.status_code == 201
    assert resp.json()["command_type"] == "EMERGENCY_LAND"
