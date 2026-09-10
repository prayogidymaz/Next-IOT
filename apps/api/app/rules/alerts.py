import json
import uuid
from datetime import UTC, datetime, timedelta
from typing import Any

import redis.asyncio as aioredis

ALERTS_QUEUE = "device:alerts"
ALERTS_HISTORY = "device:alerts:history"
DEFAULT_HISTORY_LIMIT = 500
ACTIVE_WINDOW_HOURS = 24


def _compute_severity(actual_value: float, threshold: float, operator: str) -> str:
    deviation = abs(actual_value - threshold)
    base = abs(threshold) if threshold != 0 else 1.0
    ratio = deviation / base
    if operator in (">", ">=") and actual_value >= threshold + base * 0.5:
        return "critical"
    if operator in ("<", "<=") and actual_value <= threshold - base * 0.5:
        return "critical"
    if ratio >= 0.3:
        return "warning"
    return "info"


async def emit_alert(
    redis: aioredis.Redis,
    *,
    rule_id: str,
    device_id: str,
    tenant_id: str,
    metric: str,
    operator: str,
    threshold: float,
    actual_value: float,
    action_type: str,
    reading_id: str,
    notification_channel: str | None = None,
) -> dict[str, Any]:
    severity = _compute_severity(actual_value, threshold, operator)
    payload = {
        "id": str(uuid.uuid4()),
        "event": "rule.triggered",
        "rule_id": rule_id,
        "device_id": device_id,
        "tenant_id": tenant_id,
        "metric": metric,
        "operator": operator,
        "threshold": threshold,
        "actual_value": actual_value,
        "action_type": action_type,
        "notification_channel": notification_channel or action_type,
        "reading_id": reading_id,
        "severity": severity,
        "status": "active",
        "timestamp": datetime.now(UTC).isoformat(),
    }
    serialized = json.dumps(payload)
    await redis.lpush(ALERTS_HISTORY, serialized)
    await redis.ltrim(ALERTS_HISTORY, 0, DEFAULT_HISTORY_LIMIT - 1)
    await redis.lpush(ALERTS_QUEUE, serialized)
    return payload


def _parse_timestamp(value: str | None) -> datetime | None:
    if not value:
        return None
    try:
        return datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return None


def is_alert_active(alert: dict[str, Any], *, window_hours: int = ACTIVE_WINDOW_HOURS) -> bool:
    if alert.get("status") == "resolved":
        return False
    ts = _parse_timestamp(alert.get("timestamp"))
    if ts is None:
        return True
    return datetime.now(UTC) - ts.astimezone(UTC) <= timedelta(hours=window_hours)


async def list_alerts(
    redis: aioredis.Redis,
    *,
    tenant_id: str,
    is_super_admin: bool = False,
    status: str | None = None,
    limit: int = 50,
) -> list[dict[str, Any]]:
    raw_items = await redis.lrange(ALERTS_HISTORY, 0, DEFAULT_HISTORY_LIMIT - 1)
    results: list[dict[str, Any]] = []

    for raw in raw_items:
        try:
            alert = json.loads(raw)
        except json.JSONDecodeError:
            continue

        alert_tenant = str(alert.get("tenant_id", ""))
        if not is_super_admin and alert_tenant != tenant_id:
            continue

        active = is_alert_active(alert)
        if status == "active" and not active:
            continue
        if status == "history" and active:
            continue

        results.append(alert)
        if len(results) >= limit:
            break

    return results


async def pop_alerts(redis: aioredis.Redis, count: int = 10) -> list[dict[str, Any]]:
    alerts = []
    for _ in range(count):
        raw = await redis.rpop(ALERTS_QUEUE)
        if raw is None:
            break
        alerts.append(json.loads(raw))
    return alerts
