import base64
import uuid
from datetime import UTC, datetime, timedelta

import pytest
from httpx import AsyncClient

PASSWORD = "SecurePass123!"


async def _setup_device(client: AsyncClient, slug: str, email: str) -> dict:
    reg = await client.post(
        "/auth/register",
        json={"tenant_name": f"T {slug}", "tenant_slug": slug, "email": email, "password": PASSWORD},
    )
    token = reg.json()["tokens"]["access_token"]
    create = await client.post(
        "/api/v1/devices",
        headers={"Authorization": f"Bearer {token}"},
        json={"name": "Anomaly Drone", "device_type": "drone"},
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
    return {"user_token": token, "device_id": device_id, "device_headers": device_headers}


@pytest.mark.asyncio
async def test_ingest_triggers_voltage_drop_anomaly(client: AsyncClient, unique_slug: str, unique_email: str):
    ctx = await _setup_device(client, unique_slug, unique_email)
    now = datetime.now(UTC)

    await client.post(
        "/api/v1/telemetry",
        headers=ctx["device_headers"],
        json={
            "timestamp": (now - timedelta(minutes=2)).isoformat(),
            "metrics": {"voltage": 12.0, "temperature": 30},
        },
    )
    await client.post(
        "/api/v1/telemetry",
        headers=ctx["device_headers"],
        json={
            "timestamp": now.isoformat(),
            "metrics": {"voltage": 10.0, "temperature": 30},
        },
    )

    resp = await client.get(
        "/api/v1/telemetry/anomalies",
        headers={"Authorization": f"Bearer {ctx['user_token']}"},
        params={"device_id": ctx["device_id"], "hours": 24},
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["count"] >= 1
    types = {item["anomaly_type"] for item in data["items"]}
    assert "voltage_drop" in types


@pytest.mark.asyncio
async def test_ingest_triggers_overheat_anomaly(client: AsyncClient, unique_slug: str, unique_email: str):
    ctx = await _setup_device(client, unique_slug, unique_email)
    await client.post(
        "/api/v1/telemetry",
        headers=ctx["device_headers"],
        json={
            "timestamp": datetime.now(UTC).isoformat(),
            "metrics": {"temperature": 60, "voltage": 12},
        },
    )

    resp = await client.get(
        "/api/v1/telemetry/anomalies",
        headers={"Authorization": f"Bearer {ctx['user_token']}"},
        params={"device_id": ctx["device_id"], "hours": 1},
    )
    assert resp.status_code == 200
    assert any(item["anomaly_type"] == "battery_overheat" for item in resp.json()["items"])


@pytest.mark.asyncio
async def test_anomalies_hours_validation(client: AsyncClient, unique_slug: str, unique_email: str):
    ctx = await _setup_device(client, unique_slug, unique_email)
    resp = await client.get(
        "/api/v1/telemetry/anomalies",
        headers={"Authorization": f"Bearer {ctx['user_token']}"},
        params={"device_id": ctx["device_id"], "hours": 48},
    )
    assert resp.status_code == 422


@pytest.mark.asyncio
async def test_anomalies_tenant_isolation(client: AsyncClient, unique_slug: str, unique_email: str):
    ctx = await _setup_device(client, unique_slug, unique_email)
    other = await client.post(
        "/auth/register",
        json={
            "tenant_name": "Other",
            "tenant_slug": f"other-{uuid.uuid4().hex[:6]}",
            "email": f"other-{uuid.uuid4().hex[:6]}@example.com",
            "password": PASSWORD,
        },
    )
    other_token = other.json()["tokens"]["access_token"]
    resp = await client.get(
        "/api/v1/telemetry/anomalies",
        headers={"Authorization": f"Bearer {other_token}"},
        params={"device_id": ctx["device_id"], "hours": 24},
    )
    assert resp.status_code == 404
