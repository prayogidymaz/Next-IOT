"""Normalize @xyflow/react graph JSON into automation pipeline node documents."""

from __future__ import annotations

from pydantic import JsonValue


def is_xyflow_graph(nodes: list[dict[str, JsonValue]]) -> bool:
    if not nodes:
        return False
    for node in nodes:
        if node.get("type") == "automation":
            return True
        data = node.get("data")
        if isinstance(data, dict) and "kind" in data:
            return True
    return False


def _parse_relay_pin(relay_pin: str) -> tuple[str, str]:
    raw = relay_pin.strip()
    if "/" in raw:
        device_id, channel = raw.split("/", 1)
        return device_id, f"relay_on_{channel.replace('ch', '')}"
    return raw, "relay_on"


def _xyflow_node_to_pipeline(node: dict[str, JsonValue]) -> dict[str, JsonValue]:
    data = node.get("data") or {}
    kind = str(data.get("kind", "")).lower()
    node_id = str(node.get("id"))
    label = str(data.get("label") or kind or "node")
    meta = {"label": label, "position": node.get("position"), "xyflow_type": node.get("type")}

    if kind == "trigger":
        metric = str(data.get("sensorId") or data.get("sensor_id") or "temperature")
        return {
            "id": node_id,
            "type": "TRIGGER",
            "subtype": "TELEMETRY_THRESHOLD",
            "config": {
                "metric": metric.replace("/", "_"),
                "operator": str(data.get("operator") or ">"),
                "threshold": float(data.get("threshold", 30)),
            },
            "xyflow_meta": meta,
        }

    if kind == "condition":
        metric = str(data.get("sensorId") or data.get("metric") or "temperature").replace("/", "_")
        return {
            "id": node_id,
            "type": "CONDITION",
            "subtype": "LOGIC_AND",
            "config": {
                "conditions": [
                    {
                        "metric": metric,
                        "operator": str(data.get("operator") or ">"),
                        "threshold": float(data.get("threshold", 30)),
                    }
                ]
            },
            "xyflow_meta": meta,
        }

    if kind == "action":
        relay_pin = data.get("relayPin") or data.get("relay_pin")
        notify = data.get("notifyMessage") or data.get("notify_message")
        if relay_pin:
            device_id, command = _parse_relay_pin(str(relay_pin))
            return {
                "id": node_id,
                "type": "ACTION",
                "subtype": "DEVICE_COMMAND",
                "config": {"device_id": device_id, "command": command},
                "xyflow_meta": meta,
            }
        return {
            "id": node_id,
            "type": "ACTION",
            "subtype": "TRIGGER_ALERT",
            "config": {"message": str(notify or label)},
            "xyflow_meta": meta,
        }

    if str(node.get("type", "")).upper() in {"TRIGGER", "CONDITION", "ACTION"}:
        return node

    raise ValueError(f"Unsupported xyflow node '{node_id}' (kind={kind or 'unknown'})")


def normalize_xyflow_graph(
    nodes: list[dict[str, JsonValue]],
    edges: list[dict[str, JsonValue]],
) -> tuple[list[dict[str, JsonValue]], list[dict[str, JsonValue]]]:
    normalized_nodes = [_xyflow_node_to_pipeline(node) for node in nodes]
    normalized_edges: list[dict[str, JsonValue]] = []
    for edge in edges:
        source = edge.get("source") or edge.get("from") or edge.get("from_node")
        target = edge.get("target") or edge.get("to") or edge.get("to_node")
        if not source or not target:
            continue
        normalized_edges.append({"from": str(source), "to": str(target)})
    return normalized_nodes, normalized_edges


def normalize_pipeline_payload(
    nodes_json: list[dict[str, JsonValue]],
    edges_json: list[dict[str, JsonValue]],
) -> tuple[list[dict[str, JsonValue]], list[dict[str, JsonValue]]]:
    if is_xyflow_graph(nodes_json):
        return normalize_xyflow_graph(nodes_json, edges_json)
    return nodes_json, edges_json
