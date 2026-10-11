"""Rule engine executor — load rules and run actions on events."""

from __future__ import annotations

import logging
import time
import uuid
from datetime import UTC, datetime

from pydantic import JsonValue
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from app.database import async_session
from app.models.alarm import Alarm
from app.models.device import Device
from app.models.rule import Rule, RuleTriggerType
from app.models.rule_execution_log import RuleExecutionLog, RuleExecutionStatus
from app.mqtt_publisher.protocol import MqttPublisherProtocol
from app.rules.action_runner import effective_actions, run_action
from app.rules.trigger_match import (
    cron_due,
    match_alarm_rule,
    match_attribute_change_rule,
    match_telemetry_rule,
)
from app.types.redis_client import RedisClient

logger = logging.getLogger(__name__)


def _serialize_context(context: dict[str, object]) -> dict[str, object]:
    out: dict[str, object] = {}
    for key, value in context.items():
        if isinstance(value, Device):
            out[key] = {"id": str(value.id), "name": value.name}
        elif isinstance(value, Alarm):
            out[key] = {"id": str(value.id), "alarm_type": value.alarm_type, "severity": value.severity}
        elif isinstance(value, str | int | float | bool | list | dict) or value is None:
            out[key] = value
        else:
            out[key] = str(value)
    return out


class RuleExecutor:
    def __init__(
        self,
        session_factory: async_sessionmaker[AsyncSession],
        redis: RedisClient,
        publisher: MqttPublisherProtocol,
    ) -> None:
        self._session_factory = session_factory
        self._redis = redis
        self._publisher = publisher
        self._by_trigger: dict[str, list[Rule]] = {}

    async def startup(self) -> None:
        async with self._session_factory() as db:
            await self.reload(db)
            await db.commit()

    async def reload(self, db: AsyncSession) -> None:
        rows = list(
            await db.scalars(
                select(Rule)
                .where(Rule.enabled.is_(True), Rule.is_active.is_(True))
                .order_by(Rule.priority.asc(), Rule.created_at.asc())
            )
        )
        grouped: dict[str, list[Rule]] = {t.value: [] for t in RuleTriggerType}
        for row in rows:
            trigger = row.trigger_type
            if trigger not in grouped:
                grouped[trigger] = []
            grouped[trigger].append(row)
        self._by_trigger = grouped
        logger.info(
            "Rule executor loaded %s active rules",
            sum(len(v) for v in grouped.values()),
        )

    async def on_telemetry(
        self,
        db: AsyncSession,
        *,
        device: Device,
        metric_key: str,
        value: JsonValue,
        recorded_at: datetime,
        reading_id: uuid.UUID | None = None,
    ) -> int:
        context: dict[str, object] = {
            "device": device,
            "device_id": str(device.id),
            "metric_key": metric_key,
            "value": value,
            "ts": recorded_at.isoformat(),
            "reading_id": str(reading_id) if reading_id else "",
        }
        triggered = 0
        for rule in self._by_trigger.get(RuleTriggerType.TELEMETRY, []):
            if rule.tenant_id != device.tenant_id:
                continue
            if not match_telemetry_rule(rule, device=device, metric_key=metric_key, value=value):
                continue
            await self._execute(db, rule, context)
            triggered += 1
        return triggered

    async def on_telemetry_metrics(
        self,
        db: AsyncSession,
        *,
        device: Device,
        metrics: dict[str, float],
        recorded_at: datetime,
        reading_id: uuid.UUID | None = None,
    ) -> int:
        total = 0
        for metric_key, value in metrics.items():
            total += await self.on_telemetry(
                db,
                device=device,
                metric_key=metric_key,
                value=value,
                recorded_at=recorded_at,
                reading_id=reading_id,
            )
        return total

    async def on_attribute_change(
        self,
        db: AsyncSession,
        *,
        device: Device,
        scope: str,
        key: str,
        old_value: JsonValue,
        new_value: JsonValue,
    ) -> None:
        context: dict[str, object] = {
            "device": device,
            "scope": scope,
            "key": key,
            "old_value": old_value,
            "new_value": new_value,
        }
        for rule in self._by_trigger.get(RuleTriggerType.ATTRIBUTE_CHANGE, []):
            if rule.tenant_id != device.tenant_id:
                continue
            if not match_attribute_change_rule(
                rule, device_id=device.id, scope=scope, key=key
            ):
                continue
            await self._execute(db, rule, context)

    async def on_alarm_event(
        self,
        db: AsyncSession,
        *,
        alarm: Alarm,
        event_type: str,
    ) -> None:
        context: dict[str, object] = {
            "alarm": alarm,
            "event_type": event_type,
            "severity": alarm.severity,
            "alarm_type": alarm.alarm_type,
            "status": alarm.status,
        }
        if alarm.device_id is not None:
            device = await db.scalar(select(Device).where(Device.id == alarm.device_id))
            if device is not None:
                context["device"] = device
        for rule in self._by_trigger.get(RuleTriggerType.ALARM, []):
            if rule.tenant_id != alarm.tenant_id:
                continue
            if not match_alarm_rule(
                rule,
                alarm_type=alarm.alarm_type,
                severity=alarm.severity,
                status=alarm.status,
                device_id=alarm.device_id,
            ):
                continue
            await self._execute(db, rule, context)

    async def execute_manual(self, db: AsyncSession, rule: Rule, sample_context: dict[str, object] | None) -> None:
        context = sample_context or {"now_utc": datetime.now(UTC).isoformat()}
        await self._execute(db, rule, context)

    async def dry_run(
        self,
        rule: Rule,
        sample_context: dict[str, object],
    ) -> tuple[list[dict[str, object]], list[str]]:
        from app.rules.action_runner import _action_config, _render_value_template
        from app.rules.template_engine import render_template

        errors: list[str] = []
        rendered: list[dict[str, object]] = []
        for action in effective_actions(rule):
            action_type, config = _action_config(action)
            item: dict[str, object] = {"type": action_type, "config": {}}
            try:
                if action_type == "create_alarm":
                    item["config"] = {
                        "title": render_template(str(config.get("title_template", "")), sample_context),
                        "message": render_template(str(config.get("message_template", "")), sample_context),
                    }
                elif action_type == "send_command":
                    item["config"] = {
                        "method": config.get("method"),
                        "params": _render_value_template(config.get("params_template"), sample_context),
                    }
                else:
                    item["config"] = dict(config)
                rendered.append(item)
            except ValueError as exc:
                errors.append(str(exc))
        return rendered, errors

    async def run_schedule_tick(self, db: AsyncSession, now: datetime) -> None:
        for rule in self._by_trigger.get(RuleTriggerType.SCHEDULE, []):
            cron_expr = rule.trigger_config.get("cron_expr")
            if not isinstance(cron_expr, str):
                continue
            if not cron_due(cron_expr, now, last_executed_at=rule.last_executed_at):
                continue
            context: dict[str, object] = {"now_utc": now.isoformat()}
            await self._execute(db, rule, context)

    async def _execute(self, db: AsyncSession, rule: Rule, context: dict[str, object]) -> None:
        start = time.perf_counter()
        actions_run = 0
        errors: list[str] = []
        for action in effective_actions(rule):
            try:
                await run_action(
                    db,
                    self._redis,
                    self._publisher,
                    rule=rule,
                    action=action,
                    context=context,
                )
                actions_run += 1
            except Exception as exc:
                logger.exception("Rule action failed rule_id=%s", rule.id)
                errors.append(str(exc))
        duration_ms = int((time.perf_counter() - start) * 1000)
        status = RuleExecutionStatus.SUCCESS if not errors else RuleExecutionStatus.ERROR
        if actions_run == 0 and errors:
            status = RuleExecutionStatus.ERROR
        rule.last_executed_at = datetime.now(UTC)
        rule.execution_count += 1
        rule.last_error = errors[0] if errors else None
        db.add(
            RuleExecutionLog(
                rule_id=rule.id,
                trigger_context=_serialize_context(context),
                status=status,
                actions_executed=actions_run,
                error_message="; ".join(errors) if errors else None,
                duration_ms=duration_ms,
            )
        )
        await db.flush()


_executor: RuleExecutor | None = None


def init_rule_executor(
    redis: RedisClient,
    publisher: MqttPublisherProtocol,
) -> RuleExecutor:
    global _executor
    _executor = RuleExecutor(async_session, redis, publisher)
    return _executor


def get_rule_executor() -> RuleExecutor | None:
    return _executor


async def notify_executor_reload() -> None:
    executor = get_rule_executor()
    if executor is None:
        return
    async with async_session() as db:
        await executor.reload(db)
        await db.commit()
