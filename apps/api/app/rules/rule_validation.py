"""Validate trigger/action configs and templates."""

from __future__ import annotations

import uuid
from enum import StrEnum

from pydantic import JsonValue

from app.models.rule import RuleTriggerType
from app.rules.template_engine import validate_template_string
from app.rules.trigger_match import TelemetryOperator


class RuleActionKind(StrEnum):
    CREATE_ALARM = "create_alarm"
    SEND_COMMAND = "send_command"
    SET_ATTRIBUTE = "set_attribute"
    SEND_NOTIFICATION = "send_notification"
    LOG_EVENT = "log_event"
    WEBHOOK = "webhook"
    LEGACY_ALERT = "legacy_alert"


def _require_str(config: dict[str, object], key: str, errors: list[str]) -> str | None:
    raw = config.get(key)
    if not isinstance(raw, str) or not raw.strip():
        errors.append(f"config.{key} must be a non-empty string")
        return None
    return raw


def validate_trigger_config(trigger_type: str, config: dict[str, object]) -> list[str]:
    errors: list[str] = []
    if trigger_type == RuleTriggerType.TELEMETRY:
        key = _require_str(config, "metric_key", errors)
        if key is None and "metric_key" not in config:
            errors.append("trigger_config.metric_key is required for telemetry")
        op = config.get("operator")
        if isinstance(op, str):
            allowed = {o.value for o in TelemetryOperator} | {">", "<", "==", ">=", "<="}
            if op not in allowed:
                errors.append(f"invalid telemetry operator: {op}")
        if config.get("threshold") is None:
            errors.append("trigger_config.threshold is required for telemetry")
    elif trigger_type == RuleTriggerType.ATTRIBUTE_CHANGE:
        _require_str(config, "scope", errors)
        _require_str(config, "key", errors)
    elif trigger_type == RuleTriggerType.ALARM:
        pass
    elif trigger_type == RuleTriggerType.SCHEDULE:
        cron = _require_str(config, "cron_expr", errors)
        if cron is not None:
            from croniter import croniter

            if not croniter.is_valid(cron):
                errors.append("trigger_config.cron_expr is not valid cron")
    elif trigger_type == RuleTriggerType.MANUAL:
        pass
    else:
        errors.append(f"unknown trigger_type: {trigger_type}")
    return errors


def _validate_action_config(action_type: str, config: dict[str, object]) -> list[str]:
    errors: list[str] = []
    if action_type == RuleActionKind.CREATE_ALARM:
        _require_str(config, "severity", errors)
        title = _require_str(config, "title_template", errors)
        if title is not None:
            err = validate_template_string(title)
            if err:
                errors.append(f"title_template: {err}")
        msg = config.get("message_template")
        if isinstance(msg, str):
            err = validate_template_string(msg)
            if err:
                errors.append(f"message_template: {err}")
    elif action_type == RuleActionKind.SEND_COMMAND:
        _require_str(config, "method", errors)
    elif action_type == RuleActionKind.SET_ATTRIBUTE:
        _require_str(config, "scope", errors)
        _require_str(config, "key", errors)
        if "value_template" not in config:
            errors.append("config.value_template is required for set_attribute")
    elif action_type == RuleActionKind.SEND_NOTIFICATION:
        channel_ids = config.get("channel_ids")
        if not isinstance(channel_ids, list) or not channel_ids:
            errors.append("config.channel_ids must be a non-empty list")
        else:
            for item in channel_ids:
                if not isinstance(item, str):
                    errors.append("channel_ids must be UUID strings")
                    break
                try:
                    uuid.UUID(item)
                except ValueError:
                    errors.append(f"invalid channel_id: {item}")
        title = _require_str(config, "title_template", errors)
        if title is not None:
            err = validate_template_string(title)
            if err:
                errors.append(f"title_template: {err}")
    elif action_type == RuleActionKind.LOG_EVENT:
        _require_str(config, "message_template", errors)
    elif action_type == RuleActionKind.WEBHOOK:
        _require_str(config, "url", errors)
    elif action_type == RuleActionKind.LEGACY_ALERT:
        pass
    else:
        errors.append(f"unknown action type: {action_type}")
    return errors


def validate_actions(actions: list[dict[str, JsonValue]]) -> list[str]:
    errors: list[str] = []
    if not actions:
        errors.append("actions must contain at least one action")
    for index, action in enumerate(actions):
        if not isinstance(action, dict):
            errors.append(f"actions[{index}] must be an object")
            continue
        action_type_raw = action.get("type")
        if not isinstance(action_type_raw, str):
            errors.append(f"actions[{index}].type is required")
            continue
        config_raw = action.get("config")
        config_obj: dict[str, object] = {}
        if isinstance(config_raw, dict):
            for cfg_key, cfg_val in config_raw.items():
                if isinstance(cfg_key, str):
                    config_obj[cfg_key] = cfg_val
        config = config_obj
        errors.extend(f"actions[{index}]: {e}" for e in _validate_action_config(action_type_raw, config))
    return errors
