"""Integration tests — rule executor must stay wired to event producers."""

from __future__ import annotations

import uuid
from datetime import UTC, datetime
from unittest.mock import AsyncMock, patch

import pytest
from app.database import async_session
from app.models.alarm import Alarm
from app.models.rule import Rule, RuleTriggerType
from app.models.rule_execution_log import RuleExecutionLog
from app.mqtt_publisher.noop import NoopMqttPublisher
from app.mqtt_subscriber.schemas import TelemetryMqttTopic
from app.mqtt_subscriber.service import MqttSubscriberService
from app.mqtt_subscriber.telemetry_ingest import persist_telemetry_from_mqtt
from app.rules.executor import RuleExecutor
from app.rules.telemetry_event import TelemetryRuleEvent
from httpx import AsyncClient
from sqlalchemy import select
from tests.rules.test_rule_executor_helpers import add_tenant_and_device

PASSWORD = "SecurePass123!"


@pytest.mark.asyncio
async def test_executor_startup_loads_rules(test_redis) -> None:
    tenant_id = uuid.uuid4()
    async with async_session() as db:
        await add_tenant_and_device(db, tenant_id=tenant_id)
        db.add(
            Rule(
                tenant_id=tenant_id,
                device_id=None,
                name="Sched",
                metric="m",
                operator=">",
                threshold=1,
                action_type="alert",
                enabled=True,
                is_active=True,
                trigger_type=RuleTriggerType.SCHEDULE,
                trigger_config={"cron_expr": "*/5 * * * *"},
                actions=[{"type": "log_event", "config": {"level": "info", "message_template": "tick"}}],
            )
        )
        await db.commit()
    executor = RuleExecutor(async_session, test_redis, NoopMqttPublisher())
    await executor.startup()
    assert len(executor._by_trigger.get(RuleTriggerType.SCHEDULE, [])) == 1


@pytest.mark.asyncio
async def test_subscriber_calls_executor_after_persist(test_redis) -> None:
    tenant_id = uuid.uuid4()
    device_id = uuid.uuid4()
    async with async_session() as db:
        _, _, device = await add_tenant_and_device(db, tenant_id=tenant_id, device_id=device_id)
        device.status = "online"
        rule = Rule(
            tenant_id=tenant_id,
            device_id=device_id,
            name="High Temperature Alert",
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
                        "alarm_type": "threshold_exceeded",
                        "title_template": "Temp {{ value }} on device",
                        "message_template": "threshold",
                    },
                }
            ],
        )
        db.add(rule)
        await db.commit()

    executor = RuleExecutor(async_session, test_redis, NoopMqttPublisher())
    await executor.startup()
    service = MqttSubscriberService(test_redis, rule_executor=executor)

    topic = TelemetryMqttTopic.from_mqtt_topic(f"tenants/{tenant_id}/devices/{device_id}/telemetry")
    payload = {
        "ts": datetime.now(UTC).isoformat(),
        "values": {"temperature": 50.0},
    }
    async with async_session() as db:
        result = await persist_telemetry_from_mqtt(
            db,
            test_redis,
            topic=topic,
            payload_obj=payload,
            client_id="test-subscriber",
        )
        await db.commit()
    event = result.get("rule_event")
    assert isinstance(event, TelemetryRuleEvent)
    await service._run_telemetry_rules_after_commit(event)

    async with async_session() as db:
        alarm = await db.scalar(select(Alarm).where(Alarm.rule_id == rule.id))
        assert alarm is not None
        assert alarm.source == "rule_engine"
        log = await db.scalar(select(RuleExecutionLog).where(RuleExecutionLog.rule_id == rule.id))
        assert log is not None
        assert log.status == "success"


@pytest.mark.asyncio
async def test_subscriber_skips_executor_when_not_injected(test_redis) -> None:
    """Regression guard: without injected executor, post-commit hook must not run rules."""
    service = MqttSubscriberService(test_redis, rule_executor=None)
    event = TelemetryRuleEvent(
        tenant_id=uuid.uuid4(),
        device_id=uuid.uuid4(),
        metrics={"temperature": 99.0},
        recorded_at=datetime.now(UTC),
        reading_id=uuid.uuid4(),
    )
    with patch.object(RuleExecutor, "on_telemetry", new_callable=AsyncMock) as mock_on:
        await service._run_telemetry_rules_after_commit(event)
        mock_on.assert_not_called()


@pytest.mark.asyncio
async def test_attribute_update_triggers_rule(
    client: AsyncClient, test_redis, unique_slug: str, unique_email: str
) -> None:
    reg = await client.post(
        "/auth/register",
        json={
            "tenant_name": f"T {unique_slug}",
            "tenant_slug": unique_slug,
            "email": unique_email,
            "password": PASSWORD,
        },
    )
    token = reg.json()["tokens"]["access_token"]
    create = await client.post(
        "/api/v1/devices",
        headers={"Authorization": f"Bearer {token}"},
        json={"name": "D", "device_type": "sensor"},
    )
    device_id = uuid.UUID(create.json()["device"]["id"])
    tenant_id = uuid.UUID(reg.json()["tenant_id"])

    async with async_session() as db:
        rule = Rule(
            tenant_id=tenant_id,
            device_id=device_id,
            name="Mode rule",
            metric="m",
            operator=">",
            threshold=0,
            action_type="composite",
            enabled=True,
            is_active=True,
            trigger_type=RuleTriggerType.ATTRIBUTE_CHANGE,
            trigger_config={"scope": "shared", "key": "mode"},
            actions=[{"type": "log_event", "config": {"level": "info", "message_template": "mode changed"}}],
        )
        db.add(rule)
        await db.commit()

    executor = RuleExecutor(async_session, test_redis, NoopMqttPublisher())
    await executor.startup()
    from app.rules import executor as executor_module

    executor_module._executor = executor

    put = await client.put(
        f"/api/v1/devices/{device_id}/attributes/shared/mode",
        headers={"Authorization": f"Bearer {token}"},
        json={"value": "maintenance"},
    )
    assert put.status_code == 200

    async with async_session() as db:
        log = await db.scalar(select(RuleExecutionLog).where(RuleExecutionLog.rule_id == rule.id))
        assert log is not None


@pytest.mark.asyncio
async def test_alarm_create_triggers_rule(test_redis) -> None:
    tenant_id = uuid.uuid4()
    async with async_session() as db:
        _, device_id, _ = await add_tenant_and_device(db, tenant_id=tenant_id)
        rule = Rule(
            tenant_id=tenant_id,
            device_id=None,
            name="On alarm",
            metric="m",
            operator=">",
            threshold=0,
            action_type="composite",
            enabled=True,
            is_active=True,
            trigger_type=RuleTriggerType.ALARM,
            trigger_config={"status": "active", "severity": ["major"]},
            actions=[{"type": "log_event", "config": {"level": "info", "message_template": "alarm fired"}}],
        )
        db.add(rule)
        await db.commit()

    executor = RuleExecutor(async_session, test_redis, NoopMqttPublisher())
    await executor.startup()
    from app.rules import executor as executor_module

    executor_module._executor = executor

    from app.alarms.service import upsert_alarm

    async with async_session() as db:
        await upsert_alarm(
            db,
            tenant_id=tenant_id,
            device_id=device_id,
            alarm_type="custom",
            severity="major",
            title="T",
            message="m",
            details={},
            source="manual",
            notify=False,
        )
        await db.commit()
        log = await db.scalar(select(RuleExecutionLog).where(RuleExecutionLog.rule_id == rule.id))
        assert log is not None
