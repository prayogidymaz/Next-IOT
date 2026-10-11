"""Execute individual rule actions."""

from __future__ import annotations

import logging
import uuid

import httpx
from pydantic import JsonValue
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.alarms.service import upsert_alarm
from app.attributes.broadcast import broadcast_shared_attribute_update
from app.config import settings
from app.models.device import Device
from app.models.device_attribute import DeviceAttribute, DeviceAttributeScope
from app.models.rule import Rule, RuleActionType
from app.mqtt_publisher.protocol import MqttPublisherProtocol
from app.notifications.direct_send import send_direct_notification
from app.rpc.fire_and_forget import publish_rpc_fire_and_forget
from app.rules.rule_validation import RuleActionKind
from app.rules.template_engine import render_template
from app.types.json_types import JsonObject
from app.types.redis_client import RedisClient

logger = logging.getLogger(__name__)


def _action_config(action: dict[str, object]) -> tuple[str, dict[str, object]]:
    action_type = action.get("type")
    if not isinstance(action_type, str):
        return "", {}
    config_raw = action.get("config")
    config = config_raw if isinstance(config_raw, dict) else {}
    return action_type, config


def _render_value_template(template: object, context: dict[str, object]) -> JsonValue:
    if isinstance(template, str):
        rendered = render_template(template, context)
        return rendered
    if isinstance(template, dict):
        out: JsonObject = {}
        for key, value in template.items():
            if isinstance(key, str):
                out[key] = _render_value_template(value, context)
        return out
    if isinstance(template, list):
        return [_render_value_template(item, context) for item in template]
    if isinstance(template, int | float | bool) or template is None:
        return template
    return str(template)


def effective_actions(rule: Rule) -> list[dict[str, object]]:
    stored = rule.actions
    if isinstance(stored, list) and stored:
        return [a for a in stored if isinstance(a, dict)]
    if rule.action_type == RuleActionType.ALERT:
        return [{"type": RuleActionKind.LEGACY_ALERT, "config": {}}]
    if rule.action_type == RuleActionType.WEBHOOK:
        return [{"type": RuleActionKind.WEBHOOK, "config": {"url": "", "method": "POST"}}]
    return []


async def run_action(
    db: AsyncSession,
    redis: RedisClient,
    publisher: MqttPublisherProtocol,
    *,
    rule: Rule,
    action: dict[str, object],
    context: dict[str, object],
) -> None:
    action_type, config = _action_config(action)
    device_raw = context.get("device")
    device: Device | None = device_raw if isinstance(device_raw, Device) else None

    if action_type == RuleActionKind.CREATE_ALARM:
        severity = str(config.get("severity", "warning"))
        title_tpl = str(config.get("title_template", rule.name))
        msg_tpl = str(config.get("message_template", ""))
        alarm_type = str(config.get("alarm_type", "custom"))
        title = render_template(title_tpl, context)
        message = render_template(msg_tpl, context) if msg_tpl else None
        details: dict[str, JsonValue] = {}
        for key in ("metric_key", "value", "threshold"):
            if key in context:
                val = context[key]
                if isinstance(val, str | int | float | bool | list | dict) or val is None:
                    details[key] = val
        await upsert_alarm(
            db,
            tenant_id=rule.tenant_id,
            device_id=device.id if device is not None else rule.device_id,
            alarm_type=alarm_type,
            severity=severity,
            title=title,
            message=message,
            details=details,
            source="rule_engine",
            rule_id=rule.id,
            notify=True,
        )
        return

    if action_type == RuleActionKind.LEGACY_ALERT:
        if device is None:
            return
        metric_key = str(context.get("metric_key", rule.metric))
        value_raw = context.get("value")
        actual = float(value_raw) if isinstance(value_raw, int | float) and not isinstance(value_raw, bool) else 0.0
        from app.rules.alerts import emit_alert

        await emit_alert(
            redis,
            rule_id=str(rule.id),
            device_id=str(device.id),
            tenant_id=str(rule.tenant_id),
            metric=metric_key,
            operator=rule.operator,
            threshold=rule.threshold,
            actual_value=actual,
            action_type=rule.action_type,
            reading_id=str(context.get("reading_id", "")),
        )
        return

    if action_type == RuleActionKind.SEND_COMMAND:
        if device is None:
            raise ValueError("send_command requires device in context")
        method = str(config.get("method", ""))
        params_tpl = config.get("params_template")
        params_obj = _render_value_template(params_tpl if params_tpl is not None else {}, context)
        params = params_obj if isinstance(params_obj, dict) else {}
        timeout_raw = config.get("timeout_seconds")
        timeout = int(timeout_raw) if isinstance(timeout_raw, int) else 30
        await publish_rpc_fire_and_forget(
            db,
            publisher,
            device=device,
            method=method,
            params=params,
            timeout_seconds=timeout,
        )
        return

    if action_type == RuleActionKind.SET_ATTRIBUTE:
        if device is None:
            raise ValueError("set_attribute requires device in context")
        scope = str(config.get("scope", "shared"))
        key = str(config.get("key", ""))
        value = _render_value_template(config.get("value_template"), context)
        scope_enum = DeviceAttributeScope(scope)
        row = await db.scalar(
            select(DeviceAttribute).where(
                DeviceAttribute.device_id == device.id,
                DeviceAttribute.scope == scope_enum,
                DeviceAttribute.key == key,
            )
        )
        if row is None:
            row = DeviceAttribute(
                device_id=device.id,
                tenant_id=device.tenant_id,
                scope=scope_enum,
                key=key,
                value_json=value,
                updated_by_user_id=None,
                updated_source="rule_engine",
            )
            db.add(row)
        else:
            row.value_json = value
            row.updated_source = "rule_engine"
        await db.flush()
        if scope == "shared":
            await broadcast_shared_attribute_update(
                publisher,
                tenant_id=device.tenant_id,
                device_id=device.id,
                key=key,
                value=value,
                qos=settings.attribute_shared_broadcast_qos,
            )
        return

    if action_type == RuleActionKind.SEND_NOTIFICATION:
        channel_ids_raw = config.get("channel_ids")
        if not isinstance(channel_ids_raw, list):
            return
        channel_ids = [uuid.UUID(str(item)) for item in channel_ids_raw if isinstance(item, str)]
        title = render_template(str(config.get("title_template", rule.name)), context)
        message = render_template(str(config.get("message_template", "")), context)
        severity = str(context.get("severity", "info"))
        await send_direct_notification(
            db,
            redis,
            tenant_id=rule.tenant_id,
            channel_ids=channel_ids,
            title=title,
            message=message,
            severity=severity,
            fingerprint=f"rule:{rule.id}",
        )
        return

    if action_type == RuleActionKind.LOG_EVENT:
        level = str(config.get("level", "info"))
        message = render_template(str(config.get("message_template", "")), context)
        log_fn = logger.info
        if level == "warn":
            log_fn = logger.warning
        elif level == "error":
            log_fn = logger.error
        log_fn("rule_event rule_id=%s %s", rule.id, message)
        return

    if action_type == RuleActionKind.WEBHOOK:
        url = str(config.get("url", ""))
        if not url:
            return
        method = str(config.get("method", "POST")).upper()
        headers_raw = config.get("headers")
        headers: dict[str, str] = {}
        if isinstance(headers_raw, dict):
            for key, value in headers_raw.items():
                if isinstance(key, str) and isinstance(value, str):
                    headers[key] = value
        body_tpl = config.get("body_template")
        body = _render_value_template(body_tpl if body_tpl is not None else {}, context)
        async with httpx.AsyncClient(timeout=10.0) as client:
            if method == "GET":
                await client.get(url, headers=headers)
            else:
                await client.request(method, url, headers=headers, json=body)
        return

    raise ValueError(f"Unsupported action type: {action_type}")
