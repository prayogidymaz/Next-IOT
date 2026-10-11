"""Rule engine executor tests."""

from __future__ import annotations

import uuid
from datetime import UTC, datetime
from unittest.mock import AsyncMock, patch

import pytest
from app.database import async_session
from app.models.device import Device
from app.models.rule import Rule, RuleTriggerType
from app.models.rule_execution_log import RuleExecutionLog
from app.mqtt_publisher.noop import NoopMqttPublisher
from app.rules.executor import RuleExecutor
from app.rules.rule_validation import validate_actions, validate_trigger_config
from app.rules.template_engine import validate_template_string
from app.rules.trigger_match import compare_numeric, cron_due, match_telemetry_rule
from httpx import AsyncClient
from sqlalchemy import select
from tests.rules.test_rule_executor_helpers import add_tenant_and_device

PASSWORD = "SecurePass123!"


async def _register_device(client: AsyncClient, slug: str, email: str) -> dict[str, str]:
    reg = await client.post(
        "/auth/register",
        json={"tenant_name": f"T {slug}", "tenant_slug": slug, "email": email, "password": PASSWORD},
    )
    assert reg.status_code == 201
    data = reg.json()
    token = data["tokens"]["access_token"]
    create = await client.post(
        "/api/v1/devices",
        headers={"Authorization": f"Bearer {token}"},
        json={"name": "Sensor", "device_type": "temp"},
    )
    assert create.status_code == 201
    device_id = create.json()["device"]["id"]
    return {"token": token, "tenant_id": data["tenant_id"], "device_id": device_id}


def _auth(token: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {token}"}


def test_rule_create_validates_trigger_config() -> None:
    errors = validate_trigger_config("telemetry", {"metric_key": "temp"})
    assert any("threshold" in e for e in errors)


def test_rule_create_validates_action_config() -> None:
    errors = validate_actions([{"type": "create_alarm", "config": {"severity": "major"}}])
    assert errors


def test_rule_create_rejects_invalid_jinja_template() -> None:
    err = validate_template_string("Hello {{ missing")
    assert err is not None


def test_telemetry_trigger_matches_filter() -> None:
    rule = Rule(
        tenant_id=uuid.uuid4(),
        device_id=None,
        name="r",
        metric="temperature",
        operator=">",
        threshold=30,
        action_type="alert",
        trigger_type=RuleTriggerType.TELEMETRY,
        trigger_config={"metric_key": "temperature", "operator": "gt", "threshold": 30},
    )
    device = Device(
        id=uuid.uuid4(),
        tenant_id=rule.tenant_id,
        name="D",
        device_type="temp",
        status="online",
    )
    assert match_telemetry_rule(rule, device=device, metric_key="temperature", value=35.0)


def test_telemetry_trigger_operator_gt() -> None:
    assert compare_numeric("gt", 31, 30)


def test_telemetry_trigger_operator_lt_lte_gte_eq_ne() -> None:
    assert compare_numeric("lt", 1, 2)
    assert compare_numeric("lte", 2, 2)
    assert compare_numeric("gte", 3, 3)
    assert compare_numeric("eq", 4, 4)
    assert compare_numeric("ne", 4, 5)


@pytest.mark.asyncio
async def test_executor_runs_create_alarm_action(test_redis) -> None:
    async with async_session() as db:
        tenant_id, device_id, device = await add_tenant_and_device(db)
        rule = Rule(
            tenant_id=tenant_id,
            device_id=device_id,
            name="High temp",
            metric="temperature",
            operator=">",
            threshold=30,
            action_type="composite",
            enabled=True,
            is_active=True,
            trigger_type=RuleTriggerType.TELEMETRY,
            trigger_config={"metric_key": "temperature", "operator": "gt", "threshold": 30},
            actions=[
                {
                    "type": "create_alarm",
                    "config": {
                        "severity": "major",
                        "title_template": "Temp {{ value }}",
                        "message_template": "On {{ device.name }}",
                    },
                }
            ],
        )
        db.add(rule)
        await db.commit()

        executor = RuleExecutor(async_session, test_redis, NoopMqttPublisher())
        await executor.reload(db)
        await executor.on_telemetry(
            db,
            device=device,
            metric_key="temperature",
            value=35.0,
            recorded_at=datetime.now(UTC),
        )
        await db.commit()

        from app.models.alarm import Alarm
        from sqlalchemy import select

        alarm = await db.scalar(select(Alarm).where(Alarm.tenant_id == tenant_id))
        assert alarm is not None
        assert "35" in alarm.title


@pytest.mark.asyncio
async def test_executor_runs_send_notification_action(test_redis) -> None:
    async with async_session() as db:
        tenant_id, device_id, device = await add_tenant_and_device(db)
        rule = Rule(
            tenant_id=tenant_id,
            device_id=device_id,
            name="n",
            metric="m",
            operator=">",
            threshold=1,
            action_type="composite",
            enabled=True,
            is_active=True,
            trigger_type=RuleTriggerType.MANUAL,
            trigger_config={},
            actions=[
                {
                    "type": "send_notification",
                    "config": {
                        "channel_ids": [str(uuid.uuid4())],
                        "title_template": "Hi",
                        "message_template": "There",
                    },
                }
            ],
        )
        db.add(rule)
        await db.commit()
        executor = RuleExecutor(async_session, test_redis, NoopMqttPublisher())
        await executor.reload(db)
        with patch("app.rules.action_runner.send_direct_notification", new_callable=AsyncMock) as mock_send:
            await executor.execute_manual(db, rule, {"device": device})
            mock_send.assert_awaited_once()


@pytest.mark.asyncio
async def test_executor_runs_set_attribute_action(test_redis) -> None:
    async with async_session() as db:
        tenant_id, device_id, device = await add_tenant_and_device(db)
        rule = Rule(
            tenant_id=tenant_id,
            device_id=device_id,
            name="n",
            metric="m",
            operator=">",
            threshold=1,
            action_type="composite",
            enabled=True,
            is_active=True,
            trigger_type=RuleTriggerType.MANUAL,
            trigger_config={},
            actions=[{"type": "set_attribute", "config": {"scope": "shared", "key": "mode", "value_template": "auto"}}],
        )
        db.add(rule)
        await db.commit()
        executor = RuleExecutor(async_session, test_redis, NoopMqttPublisher())
        await executor.reload(db)
        await executor.execute_manual(db, rule, {"device": device})
        await db.commit()
        from app.models.device_attribute import DeviceAttribute
        from sqlalchemy import select

        row = await db.scalar(
            select(DeviceAttribute).where(DeviceAttribute.device_id == device_id, DeviceAttribute.key == "mode")
        )
        assert row is not None


@pytest.mark.asyncio
async def test_executor_runs_send_command_action(test_redis) -> None:
    publisher = NoopMqttPublisher()
    async with async_session() as db:
        tenant_id, device_id, device = await add_tenant_and_device(db)
        rule = Rule(
            tenant_id=tenant_id,
            device_id=device_id,
            name="n",
            metric="m",
            operator=">",
            threshold=1,
            action_type="composite",
            enabled=True,
            is_active=True,
            trigger_type=RuleTriggerType.MANUAL,
            trigger_config={},
            actions=[{"type": "send_command", "config": {"method": "setRelay", "params_template": {"on": True}}}],
        )
        db.add(rule)
        await db.commit()
        executor = RuleExecutor(async_session, test_redis, publisher)
        await executor.reload(db)
        with patch("app.rules.action_runner.publish_rpc_fire_and_forget", new_callable=AsyncMock) as mock_rpc:
            await executor.execute_manual(db, rule, {"device": device})
            mock_rpc.assert_awaited_once()


@pytest.mark.asyncio
async def test_executor_isolates_action_failures(test_redis) -> None:
    async with async_session() as db:
        tenant_id, _, _ = await add_tenant_and_device(db)
        rule = Rule(
            tenant_id=tenant_id,
            device_id=None,
            name="n",
            metric="m",
            operator=">",
            threshold=1,
            action_type="composite",
            enabled=True,
            is_active=True,
            trigger_type=RuleTriggerType.MANUAL,
            trigger_config={},
            actions=[
                {"type": "send_command", "config": {"method": "x"}},
                {"type": "log_event", "config": {"level": "info", "message_template": "ok"}},
            ],
        )
        db.add(rule)
        await db.commit()
        executor = RuleExecutor(async_session, test_redis, NoopMqttPublisher())
        await executor.reload(db)
        await executor.execute_manual(db, rule, {})
        await db.commit()
        log = await db.scalar(select(RuleExecutionLog).where(RuleExecutionLog.rule_id == rule.id))
        assert log is not None
        assert log.actions_executed == 1
        assert log.status == "error"


@pytest.mark.asyncio
async def test_executor_logs_execution_success_error(test_redis) -> None:
    async with async_session() as db:
        tenant_id, _, _ = await add_tenant_and_device(db)
        rule = Rule(
            tenant_id=tenant_id,
            device_id=None,
            name="n",
            metric="m",
            operator=">",
            threshold=1,
            action_type="composite",
            enabled=True,
            is_active=True,
            trigger_type=RuleTriggerType.MANUAL,
            trigger_config={},
            actions=[{"type": "log_event", "config": {"level": "info", "message_template": "done"}}],
        )
        db.add(rule)
        await db.commit()
        executor = RuleExecutor(async_session, test_redis, NoopMqttPublisher())
        await executor.reload(db)
        await executor.execute_manual(db, rule, {})
        await db.commit()
        log = await db.scalar(select(RuleExecutionLog).where(RuleExecutionLog.rule_id == rule.id))
        assert log is not None
        assert log.status == "success"


@pytest.mark.asyncio
async def test_rule_test_endpoint_dry_run(client: AsyncClient, unique_slug: str, unique_email: str) -> None:
    ctx = await _register_device(client, unique_slug, unique_email)
    create = await client.post(
        "/api/v1/rules",
        headers=_auth(ctx["token"]),
        json={
            "name": "High temperature alert",
            "trigger_type": "telemetry",
            "trigger_config": {"metric_key": "temperature", "operator": "gt", "threshold": 30},
            "actions": [
                {
                    "type": "create_alarm",
                    "config": {
                        "severity": "major",
                        "title_template": "Temp {{ value }}°C on {{ device_name }}",
                        "message_template": "Exceeded",
                    },
                }
            ],
            "enabled": True,
        },
    )
    assert create.status_code == 201
    rule_id = create.json()["id"]
    test = await client.post(
        f"/api/v1/rules/{rule_id}/test",
        headers=_auth(ctx["token"]),
        json={"sample_context": {"value": 35, "device_name": "Sensor"}},
    )
    assert test.status_code == 200
    body = test.json()
    assert body["would_execute"] is True
    assert body["rendered_actions"]


@pytest.mark.asyncio
async def test_rule_disable_stops_execution(client: AsyncClient, unique_slug: str, unique_email: str) -> None:
    ctx = await _register_device(client, unique_slug, unique_email)
    create = await client.post(
        "/api/v1/rules",
        headers=_auth(ctx["token"]),
        json={
            "name": "R",
            "trigger_type": "manual",
            "trigger_config": {},
            "actions": [{"type": "log_event", "config": {"level": "info", "message_template": "x"}}],
        },
    )
    rule_id = create.json()["id"]
    await client.post(f"/api/v1/rules/{rule_id}/disable", headers=_auth(ctx["token"]))
    await client.post(f"/api/v1/rules/{rule_id}/execute", headers=_auth(ctx["token"]))
    logs = await client.get(f"/api/v1/rules/{rule_id}/execution-log", headers=_auth(ctx["token"]))
    assert logs.status_code == 200
    assert logs.json() == []


@pytest.mark.asyncio
async def test_rule_tenant_isolation(client: AsyncClient) -> None:
    ctx_a = await _register_device(client, f"a-{uuid.uuid4().hex[:6]}", f"a-{uuid.uuid4().hex[:6]}@example.com")
    ctx_b = await _register_device(client, f"b-{uuid.uuid4().hex[:6]}", f"b-{uuid.uuid4().hex[:6]}@example.com")
    create_b = await client.post(
        "/api/v1/rules",
        headers=_auth(ctx_b["token"]),
        json={
            "name": "B",
            "trigger_type": "manual",
            "trigger_config": {},
            "actions": [{"type": "log_event", "config": {"level": "info", "message_template": "x"}}],
        },
    )
    rule_id = create_b.json()["id"]
    cross = await client.get(f"/api/v1/rules/{rule_id}", headers=_auth(ctx_a["token"]))
    assert cross.status_code == 404


def test_schedule_trigger_fires_on_cron() -> None:
    now = datetime(2026, 1, 1, 12, 5, tzinfo=UTC)
    last = datetime(2026, 1, 1, 12, 0, tzinfo=UTC)
    assert cron_due("*/5 * * * *", now, last_executed_at=last) is True


def test_rule_fingerprint_hash_stable() -> None:
    from app.alarms.fingerprint import alarm_fingerprint, dedup_key_from_details

    fp1 = alarm_fingerprint(
        tenant_id=uuid.UUID("00000000-0000-0000-0000-000000000001"),
        device_id=uuid.UUID("00000000-0000-0000-0000-000000000002"),
        alarm_type="threshold_exceeded",
        dedup_key=dedup_key_from_details({"metric_key": "temp"}),
    )
    fp2 = alarm_fingerprint(
        tenant_id=uuid.UUID("00000000-0000-0000-0000-000000000001"),
        device_id=uuid.UUID("00000000-0000-0000-0000-000000000002"),
        alarm_type="threshold_exceeded",
        dedup_key=dedup_key_from_details({"metric_key": "temp"}),
    )
    assert fp1 == fp2
