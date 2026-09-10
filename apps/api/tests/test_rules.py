import uuid
from datetime import UTC, datetime

import pytest
import redis.asyncio as aioredis
from httpx import AsyncClient

from app.config import settings
from app.database import async_session
from app.models.rule import Rule, RuleActionType, RuleOperator
from app.rules.alerts import pop_alerts
from app.rules.evaluator import evaluate_metric

PASSWORD = "SecurePass123!"


def test_evaluate_metric_operators():
    assert evaluate_metric(RuleOperator.GT, 30.0, 25.0) is True
    assert evaluate_metric(RuleOperator.GT, 20.0, 25.0) is False
    assert evaluate_metric(RuleOperator.LT, 10.0, 15.0) is True
    assert evaluate_metric(RuleOperator.EQ, 42.0, 42.0) is True
    assert evaluate_metric(RuleOperator.GTE, 25.0, 25.0) is True
    assert evaluate_metric(RuleOperator.LTE, 24.0, 25.0) is True


async def _setup_with_rule(client: AsyncClient, slug: str, email: str, threshold: float = 25.0) -> dict:
    reg = await client.post(
        "/auth/register",
        json={"tenant_name": f"T {slug}", "tenant_slug": slug, "email": email, "password": PASSWORD},
    )
    token = reg.json()["tokens"]["access_token"]
    tenant_id = uuid.UUID(reg.json()["tenant_id"])

    create = await client.post(
        "/api/v1/devices",
        headers={"Authorization": f"Bearer {token}"},
        json={"name": "Sensor", "device_type": "temp"},
    )
    body = create.json()
    device_id = uuid.UUID(body["device"]["id"])
    prov = await client.post(
        f"/api/v1/devices/{body['device']['id']}/provision",
        json={"provisioning_token": body["provisioning_token"]},
    )
    creds = prov.json()
    import base64

    basic = base64.b64encode(f"{creds['client_id']}:{creds['client_secret']}".encode()).decode()
    device_headers = {"Authorization": f"Basic {basic}"}
    await client.post(f"/api/v1/devices/{body['device']['id']}/heartbeat", headers=device_headers, json={})

    async with async_session() as session:
        session.add(
            Rule(
                tenant_id=tenant_id,
                device_id=device_id,
                name="High temperature alert",
                metric="temperature",
                operator=RuleOperator.GT,
                threshold=threshold,
                action_type=RuleActionType.ALERT,
                is_active=True,
            )
        )
        await session.commit()

    return {
        "device_id": str(device_id),
        "device_headers": device_headers,
        "user_token": token,
    }


@pytest.mark.asyncio
async def test_rule_triggers_alert_on_telemetry(client: AsyncClient, unique_slug: str, unique_email: str):
    ctx = await _setup_with_rule(client, unique_slug, unique_email, threshold=25.0)

    resp = await client.post(
        "/api/v1/telemetry",
        headers=ctx["device_headers"],
        json={"timestamp": datetime.now(UTC).isoformat(), "metrics": {"temperature": 30.0}},
    )
    assert resp.status_code == 201
    assert resp.json()["rules_triggered"] == 1

    redis = aioredis.from_url(settings.redis_url, decode_responses=True)
    alerts = await pop_alerts(redis)
    await redis.aclose()
    assert len(alerts) == 1
    assert alerts[0]["event"] == "rule.triggered"
    assert alerts[0]["metric"] == "temperature"
    assert alerts[0]["actual_value"] == 30.0
    assert alerts[0]["threshold"] == 25.0


@pytest.mark.asyncio
async def test_rule_not_triggered_below_threshold(client: AsyncClient, unique_slug: str, unique_email: str):
    ctx = await _setup_with_rule(client, unique_slug, unique_email, threshold=50.0)

    resp = await client.post(
        "/api/v1/telemetry",
        headers=ctx["device_headers"],
        json={"timestamp": datetime.now(UTC).isoformat(), "metrics": {"temperature": 30.0}},
    )
    assert resp.status_code == 201
    assert resp.json()["rules_triggered"] == 0

    redis = aioredis.from_url(settings.redis_url, decode_responses=True)
    alerts = await pop_alerts(redis)
    await redis.aclose()
    assert len(alerts) == 0


@pytest.mark.asyncio
async def test_inactive_rule_not_evaluated(client: AsyncClient, unique_slug: str, unique_email: str):
    ctx = await _setup_with_rule(client, unique_slug, unique_email, threshold=10.0)

    async with async_session() as session:
        from sqlalchemy import update

        await session.execute(update(Rule).where(Rule.is_active.is_(True)).values(is_active=False))
        await session.commit()

    resp = await client.post(
        "/api/v1/telemetry",
        headers=ctx["device_headers"],
        json={"timestamp": datetime.now(UTC).isoformat(), "metrics": {"temperature": 99.0}},
    )
    assert resp.json()["rules_triggered"] == 0
