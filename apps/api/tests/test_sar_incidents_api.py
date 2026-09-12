import pytest
from httpx import AsyncClient

from tests.test_commands import _register_and_create_device


@pytest.mark.asyncio
async def test_sar_incidents_crud(client: AsyncClient, unique_slug: str, unique_email: str):
    ctx = await _register_and_create_device(client, unique_slug, unique_email)
    headers = {"Authorization": f"Bearer {ctx['token']}"}

    create_resp = await client.post(
        "/api/v1/mission/sar-incidents",
        headers=headers,
        json={
            "incident_type": "VEHICLE_CRASH",
            "target_lat": -6.2090,
            "target_lon": 106.8450,
            "severity": "critical",
            "assigned_device_id": ctx["device_id"],
            "message": "Vehicle crash detected by AI",
        },
    )
    assert create_resp.status_code == 201
    created = create_resp.json()
    incident_id = created["id"]
    assert created["incident_type"] == "VEHICLE_CRASH"
    assert created["status"] == "ACTIVE"
    assert created["sar_grid"]["waypoint_count"] >= 2

    list_resp = await client.get("/api/v1/mission/sar-incidents", headers=headers)
    assert list_resp.status_code == 200
    assert list_resp.json()["count"] >= 1

    active_resp = await client.get(
        "/api/v1/mission/sar-incidents",
        headers=headers,
        params={"status": "ACTIVE"},
    )
    assert all(item["status"] == "ACTIVE" for item in active_resp.json()["items"])

    patch_resp = await client.patch(
        f"/api/v1/mission/sar-incidents/{incident_id}",
        headers=headers,
        json={"status": "RESOLVED"},
    )
    assert patch_resp.status_code == 200
    assert patch_resp.json()["status"] == "RESOLVED"
    assert patch_resp.json()["resolved_at"] is not None


@pytest.mark.asyncio
async def test_regenerate_sar_grid_on_update(client: AsyncClient, unique_slug: str, unique_email: str):
    ctx = await _register_and_create_device(client, unique_slug, unique_email)
    headers = {"Authorization": f"Bearer {ctx['token']}"}

    create_resp = await client.post(
        "/api/v1/mission/sar-incidents",
        headers=headers,
        json={
            "incident_type": "PERSON_LOST",
            "target_lat": -6.21,
            "target_lon": 106.84,
            "severity": "critical",
        },
    )
    incident_id = create_resp.json()["id"]
    original_count = create_resp.json()["sar_grid"]["waypoint_count"]

    patch_resp = await client.patch(
        f"/api/v1/mission/sar-incidents/{incident_id}",
        headers=headers,
        json={"regenerate_grid": True},
    )
    assert patch_resp.status_code == 200
    assert patch_resp.json()["sar_grid"]["waypoint_count"] == original_count
