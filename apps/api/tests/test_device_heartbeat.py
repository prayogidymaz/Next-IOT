import json
import uuid

import pytest
import redis.asyncio as aioredis
from httpx import AsyncClient

from app.config import settings
from app.devices.liveness import liveness_key
from app.devices.worker import mark_stale_devices_offline

PASSWORD = "SecurePass123!"


async def _register_and_provision(client: AsyncClient, slug: str, email: str) -> dict:
    reg = await client.post(
        "/auth/register",
        json={
            "tenant_name": f"Tenant {slug}",
            "tenant_slug": slug,
            "email": email,
            "password": PASSWORD,
        },
    )
    assert reg.status_code == 201
    reg_data = reg.json()
    token = reg_data["tokens"]["access_token"]

    create = await client.post(
        "/api/v1/devices",
        headers={"Authorization": f"Bearer {token}"},
        json={"name": "HB Node", "device_type": "sensor"},
    )
    assert create.status_code == 201
    body = create.json()
    device_id = body["device"]["id"]
    prov_token = body["provisioning_token"]

    provision = await client.post(
        f"/api/v1/devices/{device_id}/provision",
        json={"provisioning_token": prov_token},
    )
    assert provision.status_code == 200
    creds = provision.json()

    return {
        "user_token": token,
        "device_id": device_id,
        "client_id": creds["client_id"],
        "client_secret": creds["client_secret"],
    }


def _basic(client_id: str, secret: str) -> dict:
    import base64

    token = base64.b64encode(f"{client_id}:{secret}".encode()).decode()
    return {"Authorization": f"Basic {token}"}


async def _pop_events() -> list[dict]:
    redis = aioredis.from_url(settings.redis_url, decode_responses=True)
    events = []
    while True:
        raw = await redis.rpop("device:events")
        if raw is None:
            break
        events.append(json.loads(raw))
    await redis.aclose()
    return events


@pytest.mark.asyncio
async def test_provision_heartbeat_online_e2e(client: AsyncClient, unique_slug: str, unique_email: str):
    ctx = await _register_and_provision(client, unique_slug, unique_email)

    hb = await client.post(
        f"/api/v1/devices/{ctx['device_id']}/heartbeat",
        headers=_basic(ctx["client_id"], ctx["client_secret"]),
        json={"firmware_version": "2.1.0", "ip": "192.168.1.50", "telemetry": {"temp": 25.5}},
    )
    assert hb.status_code == 200
    data = hb.json()
    assert data["status"] == "online"
    assert data["last_seen_at"] is not None

    detail = await client.get(
        f"/api/v1/devices/{ctx['device_id']}",
        headers={"Authorization": f"Bearer {ctx['user_token']}"},
    )
    assert detail.status_code == 200
    device = detail.json()
    assert device["status"] == "online"
    meta = {m["key"]: m["value"] for m in device["metadata"]}
    assert meta["firmware_version"] == "2.1.0"
    assert meta["ip"] == "192.168.1.50"

    events = await _pop_events()
    assert any(e["event"] == "device.online" for e in events)


@pytest.mark.asyncio
async def test_online_to_offline_via_liveness_expiry(client: AsyncClient, unique_slug: str, unique_email: str):
    ctx = await _register_and_provision(client, unique_slug, unique_email)

    hb = await client.post(
        f"/api/v1/devices/{ctx['device_id']}/heartbeat",
        headers=_basic(ctx["client_id"], ctx["client_secret"]),
        json={"firmware_version": "1.0.0"},
    )
    assert hb.status_code == 200

    redis = aioredis.from_url(settings.redis_url, decode_responses=True)
    await redis.delete(liveness_key(ctx["device_id"]))
    marked = await mark_stale_devices_offline(redis)
    await redis.aclose()
    assert marked >= 1

    detail = await client.get(
        f"/api/v1/devices/{ctx['device_id']}",
        headers={"Authorization": f"Bearer {ctx['user_token']}"},
    )
    assert detail.json()["status"] == "offline"

    events = await _pop_events()
    assert any(e["event"] == "device.offline" for e in events)


@pytest.mark.asyncio
async def test_offline_heartbeat_returns_online(client: AsyncClient, unique_slug: str, unique_email: str):
    ctx = await _register_and_provision(client, unique_slug, unique_email)

    await client.post(
        f"/api/v1/devices/{ctx['device_id']}/heartbeat",
        headers=_basic(ctx["client_id"], ctx["client_secret"]),
        json={},
    )

    redis = aioredis.from_url(settings.redis_url, decode_responses=True)
    await redis.delete(liveness_key(ctx["device_id"]))
    await mark_stale_devices_offline(redis)

    hb = await client.post(
        f"/api/v1/devices/{ctx['device_id']}/heartbeat",
        headers=_basic(ctx["client_id"], ctx["client_secret"]),
        json={},
    )
    assert hb.status_code == 200
    assert hb.json()["status"] == "online"


@pytest.mark.asyncio
async def test_deactivated_device_cannot_heartbeat(client: AsyncClient, unique_slug: str, unique_email: str):
    ctx = await _register_and_provision(client, unique_slug, unique_email)

    deactivate = await client.patch(
        f"/api/v1/devices/{ctx['device_id']}/status",
        headers={"Authorization": f"Bearer {ctx['user_token']}"},
        json={"status": "deactivated"},
    )
    assert deactivate.status_code == 200
    assert deactivate.json()["status"] == "deactivated"

    hb = await client.post(
        f"/api/v1/devices/{ctx['device_id']}/heartbeat",
        headers=_basic(ctx["client_id"], ctx["client_secret"]),
        json={},
    )
    assert hb.status_code == 403


@pytest.mark.asyncio
async def test_reactivate_deactivated_device(client: AsyncClient, unique_slug: str, unique_email: str):
    ctx = await _register_and_provision(client, unique_slug, unique_email)
    headers = {"Authorization": f"Bearer {ctx['user_token']}"}

    await client.patch(f"/api/v1/devices/{ctx['device_id']}/status", headers=headers, json={"status": "deactivated"})

    reactivate = await client.patch(
        f"/api/v1/devices/{ctx['device_id']}/status",
        headers=headers,
        json={"status": "provisioned"},
    )
    assert reactivate.status_code == 200
    assert reactivate.json()["status"] == "provisioned"

    hb = await client.post(
        f"/api/v1/devices/{ctx['device_id']}/heartbeat",
        headers=_basic(ctx["client_id"], ctx["client_secret"]),
        json={"ip": "10.0.0.1"},
    )
    assert hb.status_code == 200
    assert hb.json()["status"] == "online"


@pytest.mark.asyncio
async def test_heartbeat_device_id_mismatch(client: AsyncClient, unique_slug: str, unique_email: str):
    slug_b = f"{unique_slug}-b"
    email_b = f"b-{uuid.uuid4().hex[:6]}@example.com"
    ctx_a = await _register_and_provision(client, unique_slug, unique_email)
    ctx_b = await _register_and_provision(client, slug_b, email_b)

    resp = await client.post(
        f"/api/v1/devices/{ctx_b['device_id']}/heartbeat",
        headers=_basic(ctx_a["client_id"], ctx_a["client_secret"]),
        json={},
    )
    assert resp.status_code == 403
