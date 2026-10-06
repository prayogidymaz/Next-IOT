import uuid
from datetime import UTC, datetime, timedelta

import pytest
import redis.asyncio as aioredis
from app.database import async_session
from app.devices.liveness import liveness_key
from app.devices.worker import mark_stale_devices_offline
from app.models.telemetry_reading import TelemetryReading
from app.telemetry.cache import get_latest_telemetry
from httpx import AsyncClient
from sqlalchemy import select

PASSWORD = "SecurePass123!"


async def _register_provision_online(client: AsyncClient, slug: str, email: str) -> dict:
    reg = await client.post(
        "/auth/register",
        json={"tenant_name": f"T {slug}", "tenant_slug": slug, "email": email, "password": PASSWORD},
    )
    assert reg.status_code == 201
    token = reg.json()["tokens"]["access_token"]

    create = await client.post(
        "/api/v1/devices",
        headers={"Authorization": f"Bearer {token}"},
        json={"name": "Sensor", "device_type": "multi_sensor"},
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

    hb = await client.post(f"/api/v1/devices/{device_id}/heartbeat", headers=device_headers, json={})
    assert hb.status_code == 200

    return {
        "user_token": token,
        "device_id": device_id,
        "device_headers": device_headers,
        "client_id": creds["client_id"],
        "client_secret": creds["client_secret"],
    }


@pytest.mark.asyncio
async def test_telemetry_bulk_ingest_operator(client: AsyncClient, unique_slug: str, unique_email: str):
    ctx = await _register_provision_online(client, unique_slug, unique_email)
    ts = datetime.now(UTC).isoformat()

    resp = await client.post(
        "/api/v1/telemetry/bulk",
        headers={"Authorization": f"Bearer {ctx['user_token']}"},
        json={
            "items": [
                {
                    "device_id": ctx["device_id"],
                    "timestamp": ts,
                    "metrics": {"temperature": 27.1, "humidity": 58.0, "ph": 7.0},
                },
                {
                    "device_id": ctx["device_id"],
                    "timestamp": ts,
                    "metrics": {"temperature": 27.2, "humidity": 58.1, "ph": 7.01},
                },
            ]
        },
    )
    assert resp.status_code == 200
    body = resp.json()
    assert body["accepted"] == 2
    assert body["accepted_count"] == 2
    assert body["failed"] == 0
    assert len(body["reading_ids"]) == 2


@pytest.mark.asyncio
async def test_telemetry_ingestion_happy_path(
    client: AsyncClient, test_redis: aioredis.Redis, unique_slug: str, unique_email: str
):
    ctx = await _register_provision_online(client, unique_slug, unique_email)
    ts = datetime.now(UTC).isoformat()

    resp = await client.post(
        "/api/v1/telemetry",
        headers=ctx["device_headers"],
        json={
            "timestamp": ts,
            "metrics": {"temperature": 26.5, "humidity": 61.2, "ph": 7.1, "flow_rate": 12.3},
        },
    )
    assert resp.status_code == 201
    data = resp.json()
    assert data["device_id"] == ctx["device_id"]
    assert data["metrics"]["temperature"] == 26.5
    assert data["cached"] is True

    async with async_session() as session:
        reading = await session.scalar(
            select(TelemetryReading).where(TelemetryReading.id == uuid.UUID(data["reading_id"]))
        )
        assert reading is not None
        assert reading.metrics["humidity"] == 61.2

    cached = await get_latest_telemetry(test_redis, ctx["device_id"])
    assert cached is not None
    assert cached["metrics"]["ph"] == 7.1
    assert cached["reading_id"] == data["reading_id"]


@pytest.mark.asyncio
async def test_telemetry_rejects_offline_device(
    client: AsyncClient, test_redis: aioredis.Redis, unique_slug: str, unique_email: str
):
    ctx = await _register_provision_online(client, unique_slug, unique_email)

    await test_redis.delete(liveness_key(ctx["device_id"]))
    await mark_stale_devices_offline(test_redis)

    resp = await client.post(
        "/api/v1/telemetry",
        headers=ctx["device_headers"],
        json={"timestamp": datetime.now(UTC).isoformat(), "metrics": {"temperature": 20.0}},
    )
    assert resp.status_code == 403
    assert "online" in resp.json()["detail"].lower()


@pytest.mark.asyncio
async def test_telemetry_rejects_deactivated_device(client: AsyncClient, unique_slug: str, unique_email: str):
    ctx = await _register_provision_online(client, unique_slug, unique_email)

    deactivate = await client.patch(
        f"/api/v1/devices/{ctx['device_id']}/status",
        headers={"Authorization": f"Bearer {ctx['user_token']}"},
        json={"status": "deactivated"},
    )
    assert deactivate.status_code == 200

    resp = await client.post(
        "/api/v1/telemetry",
        headers=ctx["device_headers"],
        json={"timestamp": datetime.now(UTC).isoformat(), "metrics": {"temperature": 20.0}},
    )
    assert resp.status_code == 403


@pytest.mark.asyncio
async def test_telemetry_rejects_provisioned_without_online(client: AsyncClient, unique_slug: str, unique_email: str):
    reg = await client.post(
        "/auth/register",
        json={"tenant_name": "Test Tenant", "tenant_slug": unique_slug, "email": unique_email, "password": PASSWORD},
    )
    token = reg.json()["tokens"]["access_token"]
    create = await client.post(
        "/api/v1/devices",
        headers={"Authorization": f"Bearer {token}"},
        json={"name": "S", "device_type": "sensor"},
    )
    body = create.json()
    prov = await client.post(
        f"/api/v1/devices/{body['device']['id']}/provision",
        json={"provisioning_token": body["provisioning_token"]},
    )
    creds = prov.json()
    import base64

    basic = base64.b64encode(f"{creds['client_id']}:{creds['client_secret']}".encode()).decode()

    resp = await client.post(
        "/api/v1/telemetry",
        headers={"Authorization": f"Basic {basic}"},
        json={"timestamp": datetime.now(UTC).isoformat(), "metrics": {"temperature": 1.0}},
    )
    assert resp.status_code == 403


@pytest.mark.asyncio
async def test_telemetry_validates_timestamp(client: AsyncClient, unique_slug: str, unique_email: str):
    ctx = await _register_provision_online(client, unique_slug, unique_email)
    future = (datetime.now(UTC) + timedelta(hours=2)).isoformat()

    resp = await client.post(
        "/api/v1/telemetry",
        headers=ctx["device_headers"],
        json={"timestamp": future, "metrics": {"temperature": 20.0}},
    )
    assert resp.status_code == 422


@pytest.mark.asyncio
async def test_telemetry_requires_metrics(client: AsyncClient, unique_slug: str, unique_email: str):
    ctx = await _register_provision_online(client, unique_slug, unique_email)

    resp = await client.post(
        "/api/v1/telemetry",
        headers=ctx["device_headers"],
        json={"timestamp": datetime.now(UTC).isoformat(), "metrics": {}},
    )
    assert resp.status_code == 422


@pytest.mark.asyncio
async def test_telemetry_updates_redis_latest_cache(
    client: AsyncClient, test_redis: aioredis.Redis, unique_slug: str, unique_email: str
):
    ctx = await _register_provision_online(client, unique_slug, unique_email)

    await client.post(
        "/api/v1/telemetry",
        headers=ctx["device_headers"],
        json={"timestamp": datetime.now(UTC).isoformat(), "metrics": {"temperature": 10.0}},
    )
    await client.post(
        "/api/v1/telemetry",
        headers=ctx["device_headers"],
        json={"timestamp": datetime.now(UTC).isoformat(), "metrics": {"temperature": 99.9}},
    )

    cached = await get_latest_telemetry(test_redis, ctx["device_id"])
    assert cached["metrics"]["temperature"] == 99.9
