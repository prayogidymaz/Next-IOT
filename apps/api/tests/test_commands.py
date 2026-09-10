import json
import uuid

import pytest
import redis.asyncio as aioredis
from httpx import AsyncClient

from app.auth.security import hash_password
from app.commands.events import DEVICE_COMMANDS_CHANNEL
from app.config import settings
from app.database import async_session
from app.models.user import User

PASSWORD = "SecurePass123!"


async def _register_and_create_device(client: AsyncClient, slug: str, email: str) -> dict:
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
    data = reg.json()
    token = data["tokens"]["access_token"]

    create = await client.post(
        "/api/v1/devices",
        headers={"Authorization": f"Bearer {token}"},
        json={"name": "Mission Drone", "device_type": "drone"},
    )
    assert create.status_code == 201
    return {"token": token, "device_id": create.json()["device"]["id"], "tenant_id": data["tenant_id"]}


@pytest.mark.asyncio
async def test_dispatch_go_to_mission_command(client: AsyncClient, unique_slug: str, unique_email: str):
    ctx = await _register_and_create_device(client, unique_slug, unique_email)

    redis = aioredis.from_url(settings.redis_url, decode_responses=True)
    pubsub = redis.pubsub()
    await pubsub.subscribe(DEVICE_COMMANDS_CHANNEL)
    for _ in range(50):
        sub_msg = await pubsub.get_message(ignore_subscribe_messages=False, timeout=0.1)
        if sub_msg and sub_msg.get("type") == "subscribe":
            break

    payload = {
        "command_type": "GO_TO_MISSION",
        "params": {
            "altitude_m": 60,
            "waypoints": [
                {"sequence": 1, "lat": -6.2088, "lon": 106.8456},
                {"sequence": 2, "lat": -6.2100, "lon": 106.8500},
            ],
        },
    }
    resp = await client.post(
        f"/api/v1/devices/{ctx['device_id']}/commands",
        headers={"Authorization": f"Bearer {ctx['token']}"},
        json=payload,
    )
    assert resp.status_code == 201
    body = resp.json()
    assert body["command_type"] == "GO_TO_MISSION"
    assert body["status"] == "dispatched"
    assert len(body["params"]["waypoints"]) == 2

    message = None
    for _ in range(20):
        message = await pubsub.get_message(ignore_subscribe_messages=True, timeout=0.25)
        if message is not None:
            break
    assert message is not None
    published = json.loads(message["data"])
    assert published["command_type"] == "GO_TO_MISSION"
    assert published["device_id"] == ctx["device_id"]

    events = []
    while True:
        raw = await redis.rpop("device:events")
        if raw is None:
            break
        events.append(json.loads(raw))
    assert any(e.get("event") == "command.dispatched" for e in events)

    await pubsub.unsubscribe(DEVICE_COMMANDS_CHANNEL)
    await pubsub.aclose()
    await redis.aclose()


@pytest.mark.asyncio
async def test_dispatch_rtl_command(client: AsyncClient, unique_slug: str, unique_email: str):
    ctx = await _register_and_create_device(client, unique_slug, unique_email)

    resp = await client.post(
        f"/api/v1/devices/{ctx['device_id']}/commands",
        headers={"Authorization": f"Bearer {ctx['token']}"},
        json={"command_type": "RTL", "params": {}},
    )
    assert resp.status_code == 201
    assert resp.json()["command_type"] == "RTL"


@pytest.mark.asyncio
async def test_dispatch_command_denied_for_viewer(client: AsyncClient, unique_slug: str, unique_email: str):
    ctx = await _register_and_create_device(client, unique_slug, unique_email)
    viewer_email = f"viewer-{uuid.uuid4().hex[:6]}@example.com"

    async with async_session() as session:
        session.add(
            User(
                tenant_id=uuid.UUID(ctx["tenant_id"]),
                email=viewer_email,
                password_hash=hash_password(PASSWORD),
                role="viewer",
            )
        )
        await session.commit()

    login = await client.post("/auth/login", json={"email": viewer_email, "password": PASSWORD})
    assert login.status_code == 200
    viewer_token = login.json()["access_token"]

    resp = await client.post(
        f"/api/v1/devices/{ctx['device_id']}/commands",
        headers={"Authorization": f"Bearer {viewer_token}"},
        json={"command_type": "RTL", "params": {}},
    )
    assert resp.status_code == 403


@pytest.mark.asyncio
async def test_dispatch_go_to_waypoint_validation(client: AsyncClient, unique_slug: str, unique_email: str):
    ctx = await _register_and_create_device(client, unique_slug, unique_email)

    resp = await client.post(
        f"/api/v1/devices/{ctx['device_id']}/commands",
        headers={"Authorization": f"Bearer {ctx['token']}"},
        json={"command_type": "GO_TO_WAYPOINT", "params": {"lat": -6.2}},
    )
    assert resp.status_code == 422
