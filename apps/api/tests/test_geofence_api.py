import pytest
from httpx import AsyncClient

from tests.test_anomaly_detection import _setup_device
from tests.test_commands import _register_and_create_device


SAMPLE_POLYGON = [
    {"lat": -6.2100, "lon": 106.8440},
    {"lat": -6.2100, "lon": 106.8460},
    {"lat": -6.2080, "lon": 106.8460},
    {"lat": -6.2080, "lon": 106.8440},
]


@pytest.mark.asyncio
async def test_geofence_crud(client: AsyncClient, unique_slug: str, unique_email: str):
    ctx = await _register_and_create_device(client, unique_slug, unique_email)
    headers = {"Authorization": f"Bearer {ctx['token']}"}

    create_resp = await client.post(
        "/api/v1/mission/geofence",
        headers=headers,
        json={
            "name": "No-Fly Sector A",
            "polygon_coords": SAMPLE_POLYGON,
            "min_altitude": 0,
            "max_altitude": 120,
            "action_on_breach": "RTL",
        },
    )
    assert create_resp.status_code == 201
    created = create_resp.json()
    zone_id = created["id"]
    assert created["name"] == "No-Fly Sector A"
    assert created["action_on_breach"] == "RTL"
    assert len(created["polygon_coords"]) == 4

    list_resp = await client.get("/api/v1/mission/geofence", headers=headers)
    assert list_resp.status_code == 200
    assert list_resp.json()["count"] == 1

    get_resp = await client.get(f"/api/v1/mission/geofence/{zone_id}", headers=headers)
    assert get_resp.status_code == 200
    assert get_resp.json()["id"] == zone_id

    update_resp = await client.put(
        f"/api/v1/mission/geofence/{zone_id}",
        headers=headers,
        json={"name": "No-Fly Sector A Updated", "action_on_breach": "LAND"},
    )
    assert update_resp.status_code == 200
    assert update_resp.json()["name"] == "No-Fly Sector A Updated"
    assert update_resp.json()["action_on_breach"] == "LAND"

    delete_resp = await client.delete(f"/api/v1/mission/geofence/{zone_id}", headers=headers)
    assert delete_resp.status_code == 204

    list_after = await client.get("/api/v1/mission/geofence", headers=headers)
    assert list_after.json()["count"] == 0


@pytest.mark.asyncio
async def test_geofence_breach_on_telemetry_ingest(client: AsyncClient, unique_slug: str, unique_email: str):
    ctx = await _setup_device(client, unique_slug, unique_email)
    headers = {"Authorization": f"Bearer {ctx['user_token']}"}
    device_headers = ctx["device_headers"]

    await client.post(
        "/api/v1/mission/geofence",
        headers=headers,
        json={
            "name": "Restricted Box",
            "polygon_coords": SAMPLE_POLYGON,
            "min_altitude": 0,
            "max_altitude": 120,
            "action_on_breach": "WARN",
        },
    )

    from datetime import UTC, datetime

    ingest = await client.post(
        "/api/v1/telemetry",
        headers=device_headers,
        json={
            "timestamp": datetime.now(UTC).isoformat(),
            "metrics": {
                "latitude": -6.2090,
                "longitude": 106.8450,
                "altitude": 50.0,
                "voltage": 12.5,
            },
        },
    )
    assert ingest.status_code == 201

    anomalies = await client.get(
        "/api/v1/telemetry/anomalies",
        headers=headers,
        params={"device_id": ctx["device_id"], "hours": 24},
    )
    assert anomalies.status_code == 200
    types = {item["anomaly_type"] for item in anomalies.json()["items"]}
    assert "geofence_breach" in types
