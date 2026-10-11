"""Match rule triggers against event context."""

from __future__ import annotations

import uuid
from datetime import datetime
from enum import StrEnum

from pydantic import JsonValue

from app.models.device import Device
from app.models.rule import Rule, RuleOperator


class TelemetryOperator(StrEnum):
    GT = "gt"
    LT = "lt"
    EQ = "eq"
    GTE = "gte"
    LTE = "lte"
    NE = "ne"


_LEGACY_TO_TELEMETRY: dict[str, TelemetryOperator] = {
    RuleOperator.GT: TelemetryOperator.GT,
    RuleOperator.LT: TelemetryOperator.LT,
    RuleOperator.EQ: TelemetryOperator.EQ,
    RuleOperator.GTE: TelemetryOperator.GTE,
    RuleOperator.LTE: TelemetryOperator.LTE,
    ">": TelemetryOperator.GT,
    "<": TelemetryOperator.LT,
    "==": TelemetryOperator.EQ,
    ">=": TelemetryOperator.GTE,
    "<=": TelemetryOperator.LTE,
}


def _config_str(config: dict[str, object], key: str) -> str | None:
    raw = config.get(key)
    return raw if isinstance(raw, str) else None


def _config_uuid(config: dict[str, object], key: str) -> uuid.UUID | None:
    raw = _config_str(config, key)
    if raw is None:
        return None
    try:
        return uuid.UUID(raw)
    except ValueError:
        return None


def compare_numeric(operator: str, actual: float, threshold: float) -> bool:
    op = _LEGACY_TO_TELEMETRY.get(operator)
    if op is None:
        try:
            op = TelemetryOperator(operator)
        except ValueError:
            return False
    if op == TelemetryOperator.GT:
        return actual > threshold
    if op == TelemetryOperator.LT:
        return actual < threshold
    if op == TelemetryOperator.GTE:
        return actual >= threshold
    if op == TelemetryOperator.LTE:
        return actual <= threshold
    if op == TelemetryOperator.EQ:
        return actual == threshold
    if op == TelemetryOperator.NE:
        return actual != threshold
    return False


def _numeric_threshold(config: dict[str, object]) -> float | None:
    raw = config.get("threshold")
    if isinstance(raw, bool):
        return None
    if isinstance(raw, int | float):
        return float(raw)
    if isinstance(raw, str):
        try:
            return float(raw)
        except ValueError:
            return None
    return None


def match_telemetry_rule(
    rule: Rule,
    *,
    device: Device,
    metric_key: str,
    value: JsonValue,
) -> bool:
    config = rule.trigger_config
    cfg_device = _config_uuid(config, "device_id")
    if cfg_device is not None and cfg_device != device.id:
        return False
    if rule.device_id is not None and rule.device_id != device.id:
        return False

    profile_raw = config.get("device_profile_id")
    if isinstance(profile_raw, str):
        try:
            profile_id = uuid.UUID(profile_raw)
            if device.profile_id != profile_id:
                return False
        except ValueError:
            return False

    expected_key = _config_str(config, "metric_key") or rule.metric
    if expected_key != metric_key:
        return False

    if not isinstance(value, int | float) or isinstance(value, bool):
        return False
    actual = float(value)
    threshold = _numeric_threshold(config)
    if threshold is None:
        threshold = rule.threshold
    operator = _config_str(config, "operator") or rule.operator
    return compare_numeric(operator, actual, threshold)


def match_attribute_change_rule(
    rule: Rule,
    *,
    device_id: uuid.UUID,
    scope: str,
    key: str,
) -> bool:
    config = rule.trigger_config
    cfg_device = _config_uuid(config, "device_id")
    if cfg_device is not None and cfg_device != device_id:
        return False
    if rule.device_id is not None and rule.device_id != device_id:
        return False
    cfg_scope = _config_str(config, "scope")
    if cfg_scope is not None and cfg_scope != scope:
        return False
    cfg_key = _config_str(config, "key")
    if cfg_key is not None and cfg_key != key:
        return False
    return True


def match_alarm_rule(
    rule: Rule,
    *,
    alarm_type: str,
    severity: str,
    status: str,
    device_id: uuid.UUID | None,
) -> bool:
    config = rule.trigger_config
    cfg_device = _config_uuid(config, "device_id")
    if cfg_device is not None and device_id != cfg_device:
        return False
    severities_raw = config.get("severity")
    if isinstance(severities_raw, list):
        allowed = {s for s in severities_raw if isinstance(s, str)}
        if allowed and severity not in allowed:
            return False
    type_raw = _config_str(config, "alarm_type")
    if type_raw is not None and type_raw != alarm_type:
        return False
    status_raw = _config_str(config, "status")
    if status_raw is not None and status_raw != status:
        return False
    return True


def cron_due(cron_expr: str, now: datetime, *, last_executed_at: datetime | None) -> bool:
    from datetime import timedelta

    from croniter import croniter

    base = last_executed_at if last_executed_at is not None else now - timedelta(minutes=1)
    itr = croniter(cron_expr, base)
    next_run = itr.get_next(datetime)
    if next_run.tzinfo is None and now.tzinfo is not None:
        next_run = next_run.replace(tzinfo=now.tzinfo)
    return bool(next_run <= now)
