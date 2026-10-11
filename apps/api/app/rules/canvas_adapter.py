"""Convert Automation Studio canvas export to executor rule payloads."""

from __future__ import annotations

from pydantic import JsonValue


def canvas_to_rule_payload(document: dict[str, JsonValue]) -> dict[str, JsonValue] | None:
    """Best-effort mapping from xyflow canvas nodes to telemetry rule + create_alarm action."""
    nodes_raw = document.get("nodes")
    if not isinstance(nodes_raw, list):
        return None
    trigger_metric: str | None = None
    operator = "gt"
    threshold = 0.0
    title = "Automation alert"
    message = "Triggered from Automation Studio"
    for node in nodes_raw:
        if not isinstance(node, dict):
            continue
        data = node.get("data")
        if not isinstance(data, dict):
            continue
        kind = data.get("kind")
        sensor_raw = data.get("sensorId")
        if kind == "trigger" and isinstance(sensor_raw, str):
            trigger_metric = sensor_raw.split("/")[-1]
        if kind == "condition":
            op = data.get("operator")
            if op == ">":
                operator = "gt"
            elif op == "<":
                operator = "lt"
            elif op == "==":
                operator = "eq"
            thr = data.get("threshold")
            if isinstance(thr, int | float) and not isinstance(thr, bool):
                threshold = float(thr)
        notify_raw = data.get("notifyMessage")
        if kind == "action" and isinstance(notify_raw, str):
            message = notify_raw
            label_raw = data.get("label")
            if isinstance(label_raw, str):
                title = label_raw
    if trigger_metric is None:
        return None
    return {
        "name": str(document.get("name", "Studio rule")),
        "trigger_type": "telemetry",
        "trigger_config": {
            "metric_key": trigger_metric,
            "operator": operator,
            "threshold": threshold,
        },
        "actions": [
            {
                "type": "create_alarm",
                "config": {
                    "severity": "major",
                    "title_template": title,
                    "message_template": message,
                },
            }
        ],
        "enabled": True,
    }
