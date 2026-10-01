import pytest
import redis.asyncio as aioredis
from app.config import settings
from app.database import async_session
from app.models.telemetry_reading import TelemetryReading
from app.seed import ensure_default_admin
from app.seed_telemetry import DEMO_DEVICE_NAME, ensure_demo_telemetry, run_telemetry_seed
from httpx import AsyncClient
from sqlalchemy import func, select


@pytest.mark.asyncio
async def test_seed_demo_telemetry_is_idempotent(client: AsyncClient, test_redis: aioredis.Redis):
    async with async_session() as db:
        await ensure_default_admin(db)

    created = await run_telemetry_seed(test_redis)
    assert created is True

    async with async_session() as db:
        created_again = await ensure_demo_telemetry(db, test_redis)
        assert created_again is False

        count = await db.scalar(select(func.count()).select_from(TelemetryReading))
        assert count is not None and count >= 300


@pytest.mark.asyncio
async def test_seeded_telemetry_queryable_by_admin(client: AsyncClient, test_redis: aioredis.Redis):
    async with async_session() as db:
        await ensure_default_admin(db)
    await run_telemetry_seed(test_redis)

    login = await client.post(
        "/auth/login",
        json={"email": settings.seed_admin_email, "password": settings.seed_admin_password},
    )
    token = login.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    devices = await client.get("/api/v1/devices", headers=headers)
    assert devices.status_code == 200
    demo = next(d for d in devices.json() if d["name"] == DEMO_DEVICE_NAME)
    device_id = demo["id"]

    latest = await client.get(
        f"/api/v1/devices/{device_id}/telemetry/latest",
        headers=headers,
    )
    assert latest.status_code == 200
    assert latest.json()["metrics"]["temperature"] is not None

    history = await client.get(
        f"/api/v1/devices/{device_id}/telemetry/history",
        headers=headers,
        params={"limit": 20},
    )
    assert history.status_code == 200
    assert history.json()["count"] >= 20
