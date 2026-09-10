import uuid
from datetime import UTC, datetime, timedelta

import pytest
from httpx import AsyncClient

PASSWORD = "SecurePass123!"


async def _setup_online_device(client: AsyncClient, slug: str, email: str) -> dict:
    reg = await client.post(
        "/auth/register",
        json={"tenant_name": f"T {slug}", "tenant_slug": slug, "email": email, "password": PASSWORD},
    )
    token = reg.json()["tokens"]["access_token"]
    create = await client.post(
        "/api/v1/devices",
        headers={"Authorization": f"Bearer {token}"},
        json={"name": "Sensor", "device_type": "multi"},
    )
    body = create.json()
    device_id = body["device"]["id"]
    prov = await client.post(
        f"/api/v1/devices/{device_id}/provision",
        json={"provisioning_token": body["provisioning_token"]},
    )
    creds = prov.json()
    import base64

    basic = base64.b64encode(f"{creds['client_id']}:{creds['client_secret']}".encode()).decode()
    device_headers = {"Authorization": f"Basic {basic}"}
    await client.post(f"/api/v1/devices/{device_id}/heartbeat", headers=device_headers, json={})

    ts1 = (datetime.now(UTC) - timedelta(minutes=10)).isoformat()
    ts2 = datetime.now(UTC).isoformat()
    await client.post(
        "/api/v1/telemetry",
        headers=device_headers,
        json={"timestamp": ts1, "metrics": {"temperature": 20.0}},
    )
    await client.post(
        "/api/v1/telemetry",
        headers=device_headers,
        json={"timestamp": ts2, "metrics": {"temperature": 30.0, "humidity": 55.0}},
    )

    return {"user_token": token, "device_id": device_id, "device_headers": device_headers}


@pytest.mark.asyncio
async def test_get_latest_telemetry(client: AsyncClient, unique_slug: str, unique_email: str):
    ctx = await _setup_online_device(client, unique_slug, unique_email)

    resp = await client.get(
        f"/api/v1/devices/{ctx['device_id']}/telemetry/latest",
        headers={"Authorization": f"Bearer {ctx['user_token']}"},
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["source"] == "redis"
    assert data["metrics"]["temperature"] == 30.0
    assert data["metrics"]["humidity"] == 55.0


@pytest.mark.asyncio
async def test_get_latest_telemetry_tenant_isolation(client: AsyncClient):
    slug_a = f"a-{uuid.uuid4().hex[:6]}"
    slug_b = f"b-{uuid.uuid4().hex[:6]}"
    ctx_a = await _setup_online_device(client, slug_a, f"a-{uuid.uuid4().hex[:6]}@example.com")
    ctx_b = await _setup_online_device(client, slug_b, f"b-{uuid.uuid4().hex[:6]}@example.com")

    denied = await client.get(
        f"/api/v1/devices/{ctx_b['device_id']}/telemetry/latest",
        headers={"Authorization": f"Bearer {ctx_a['user_token']}"},
    )
    assert denied.status_code == 404


@pytest.mark.asyncio
async def test_get_telemetry_history_with_filters(client: AsyncClient, unique_slug: str, unique_email: str):
    ctx = await _setup_online_device(client, unique_slug, unique_email)
    now = datetime.now(UTC)
    start = (now - timedelta(hours=1)).isoformat()
    end = now.isoformat()

    resp = await client.get(
        f"/api/v1/devices/{ctx['device_id']}/telemetry/history",
        headers={"Authorization": f"Bearer {ctx['user_token']}"},
        params={"start_time": start, "end_time": end, "limit": 10},
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["count"] == 2
    assert len(data["items"]) == 2
    assert data["items"][0]["metrics"]["temperature"] == 30.0


@pytest.mark.asyncio
async def test_get_latest_requires_auth(client: AsyncClient, unique_slug: str, unique_email: str):
    ctx = await _setup_online_device(client, unique_slug, unique_email)
    resp = await client.get(f"/api/v1/devices/{ctx['device_id']}/telemetry/latest")
    assert resp.status_code == 401
