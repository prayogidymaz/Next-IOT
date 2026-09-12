import uuid
from datetime import UTC, datetime, timedelta

import base64

import pytest
from httpx import AsyncClient

PASSWORD = "SecurePass123!"


async def _setup_device_with_gps_telemetry(client: AsyncClient, slug: str, email: str) -> dict:
    reg = await client.post(
        "/auth/register",
        json={"tenant_name": f"T {slug}", "tenant_slug": slug, "email": email, "password": PASSWORD},
    )
    token = reg.json()["tokens"]["access_token"]
    create = await client.post(
        "/api/v1/devices",
        headers={"Authorization": f"Bearer {token}"},
        json={"name": "Export Drone", "device_type": "drone"},
    )
    body = create.json()
    device_id = body["device"]["id"]
    prov = await client.post(
        f"/api/v1/devices/{device_id}/provision",
        json={"provisioning_token": body["provisioning_token"]},
    )
    creds = prov.json()
    basic = base64.b64encode(f"{creds['client_id']}:{creds['client_secret']}".encode()).decode()
    device_headers = {"Authorization": f"Basic {basic}"}
    await client.post(f"/api/v1/devices/{device_id}/heartbeat", headers=device_headers, json={})

    now = datetime.now(UTC)
    await client.post(
        "/api/v1/telemetry",
        headers=device_headers,
        json={
            "timestamp": (now - timedelta(minutes=5)).isoformat(),
            "metrics": {"latitude": -6.2, "longitude": 106.8, "altitude": 50, "speed": 10, "voltage": 12.1},
        },
    )
    await client.post(
        "/api/v1/telemetry",
        headers=device_headers,
        json={
            "timestamp": now.isoformat(),
            "metrics": {"latitude": -6.201, "longitude": 106.801, "altitude": 55, "speed": 18, "voltage": 11.4},
        },
    )

    return {"user_token": token, "device_id": device_id}


@pytest.mark.asyncio
async def test_telemetry_export_csv(client: AsyncClient, unique_slug: str, unique_email: str):
    ctx = await _setup_device_with_gps_telemetry(client, unique_slug, unique_email)
    resp = await client.get(
        "/api/v1/telemetry/export",
        headers={"Authorization": f"Bearer {ctx['user_token']}"},
        params={"device_id": ctx["device_id"], "format": "csv", "hours": 24},
    )
    assert resp.status_code == 200
    assert "text/csv" in resp.headers["content-type"]
    assert "attachment" in resp.headers["content-disposition"]
    assert "-6.2" in resp.text


@pytest.mark.asyncio
async def test_telemetry_export_kml(client: AsyncClient, unique_slug: str, unique_email: str):
    ctx = await _setup_device_with_gps_telemetry(client, unique_slug, unique_email)
    resp = await client.get(
        "/api/v1/telemetry/export",
        headers={"Authorization": f"Bearer {ctx['user_token']}"},
        params={"device_id": ctx["device_id"], "format": "kml", "hours": 24},
    )
    assert resp.status_code == 200
    assert "kml" in resp.headers["content-type"]
    assert "<kml" in resp.text


@pytest.mark.asyncio
async def test_telemetry_analytics_summary(client: AsyncClient, unique_slug: str, unique_email: str):
    ctx = await _setup_device_with_gps_telemetry(client, unique_slug, unique_email)
    resp = await client.get(
        "/api/v1/telemetry/analytics",
        headers={"Authorization": f"Bearer {ctx['user_token']}"},
        params={"device_id": ctx["device_id"], "hours": 24},
    )
    assert resp.status_code == 200
    body = resp.json()
    assert body["reading_count"] == 2
    assert body["max_speed_m_s"] == 18.0
    assert body["min_voltage_v"] == 11.4
    assert body["total_distance_m"] > 0
    assert body["anomaly_count"] >= 0
