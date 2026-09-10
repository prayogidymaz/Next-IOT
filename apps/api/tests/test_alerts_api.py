import uuid
from datetime import UTC, datetime

import pytest
import redis.asyncio as aioredis
from httpx import AsyncClient

from app.config import settings
from app.rules.alerts import ALERTS_HISTORY, emit_alert, list_alerts

PASSWORD = "SecurePass123!"


@pytest.mark.asyncio
async def test_list_alerts_filters_by_tenant_and_status(client: AsyncClient, unique_slug: str, unique_email: str):
    reg = await client.post(
        "/auth/register",
        json={"tenant_name": "A Co", "tenant_slug": unique_slug, "email": unique_email, "password": PASSWORD},
    )
    token = reg.json()["tokens"]["access_token"]
    tenant_id = reg.json()["tenant_id"]

    redis = aioredis.from_url(settings.redis_url, decode_responses=True)
    await redis.delete(ALERTS_HISTORY)

    await emit_alert(
        redis,
        rule_id="r1",
        device_id="d1",
        tenant_id=tenant_id,
        metric="temperature",
        operator=">",
        threshold=25.0,
        actual_value=45.0,
        action_type="alert",
        reading_id="rd1",
        notification_channel="telegram",
    )
    await redis.aclose()

    resp = await client.get(
        "/api/v1/alerts",
        headers={"Authorization": f"Bearer {token}"},
        params={"status": "active"},
    )
    assert resp.status_code == 200
    body = resp.json()
    assert body["count"] == 1
    assert body["items"][0]["severity"] == "critical"
    assert body["items"][0]["metric"] == "temperature"


@pytest.mark.asyncio
async def test_alerts_summary_endpoint(client: AsyncClient, unique_slug: str, unique_email: str):
    reg = await client.post(
        "/auth/register",
        json={"tenant_name": "B Co", "tenant_slug": unique_slug, "email": unique_email, "password": PASSWORD},
    )
    token = reg.json()["tokens"]["access_token"]
    tenant_id = reg.json()["tenant_id"]

    redis = aioredis.from_url(settings.redis_url, decode_responses=True)
    await redis.delete(ALERTS_HISTORY)
    await emit_alert(
        redis,
        rule_id="r1",
        device_id="d1",
        tenant_id=tenant_id,
        metric="humidity",
        operator=">",
        threshold=50.0,
        actual_value=55.0,
        action_type="webhook",
        reading_id="rd1",
        notification_channel="webhook",
    )
    await redis.aclose()

    resp = await client.get(
        "/api/v1/alerts/summary",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp.status_code == 200
    assert resp.json()["active_count"] == 1


@pytest.mark.asyncio
async def test_list_all_rules_endpoint(client: AsyncClient, unique_slug: str, unique_email: str):
    reg = await client.post(
        "/auth/register",
        json={"tenant_name": "C Co", "tenant_slug": unique_slug, "email": unique_email, "password": PASSWORD},
    )
    token = reg.json()["tokens"]["access_token"]

    create = await client.post(
        "/api/v1/devices",
        headers={"Authorization": f"Bearer {token}"},
        json={"name": "Sensor", "device_type": "temp"},
    )
    device_id = create.json()["device"]["id"]

    created = await client.post(
        "/api/v1/rules",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "device_id": device_id,
            "name": "High temp",
            "metric": "temperature",
            "operator": ">",
            "threshold": 45.0,
            "action_type": "alert",
        },
    )
    assert created.status_code == 201

    listed = await client.get("/api/v1/rules", headers={"Authorization": f"Bearer {token}"})
    assert listed.status_code == 200
    assert len(listed.json()) == 1
