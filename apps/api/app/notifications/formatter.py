from html import escape
from typing import Any


def format_telegram_html(alert: dict[str, Any]) -> str:
    """Format alert payload as Telegram HTML message."""
    event = escape(str(alert.get("event", "alert")))
    metric = escape(str(alert.get("metric", "—")))
    device_id = escape(str(alert.get("device_id", "—")))
    tenant_id = escape(str(alert.get("tenant_id", "—")))
    timestamp = escape(str(alert.get("timestamp", "—")))

    lines = [
        f"<b>Next-IOT Alert</b>",
        f"<b>Event:</b> {event}",
        f"<b>Device:</b> <code>{device_id}</code>",
        f"<b>Tenant:</b> <code>{tenant_id}</code>",
    ]

    if "metric" in alert:
        operator = escape(str(alert.get("operator", "")))
        threshold = alert.get("threshold")
        actual = alert.get("actual_value")
        lines.append(f"<b>Metric:</b> {metric}")
        if operator and threshold is not None and actual is not None:
            lines.append(f"<b>Condition:</b> {metric} {operator} {threshold}")
            lines.append(f"<b>Actual:</b> <code>{actual}</code>")

    if "message" in alert:
        lines.append(f"<b>Message:</b> {escape(str(alert['message']))}")

    lines.append(f"<b>Time:</b> {timestamp}")
    return "\n".join(lines)


def build_webhook_payload(alert: dict[str, Any]) -> dict[str, Any]:
    """Standard JSON payload for webhook receivers."""
    return {
        "source": "next-iot",
        "event": alert.get("event", "alert"),
        "device_id": alert.get("device_id"),
        "tenant_id": alert.get("tenant_id"),
        "rule_id": alert.get("rule_id"),
        "metric": alert.get("metric"),
        "operator": alert.get("operator"),
        "threshold": alert.get("threshold"),
        "actual_value": alert.get("actual_value"),
        "action_type": alert.get("action_type"),
        "reading_id": alert.get("reading_id"),
        "message": alert.get("message"),
        "timestamp": alert.get("timestamp"),
    }
