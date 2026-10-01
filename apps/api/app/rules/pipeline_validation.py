"""Validate automation pipeline JSON graphs (structure, cycles, required config)."""

from __future__ import annotations

from pydantic import JsonValue

_REQUIRED_TRIGGER = {
    "TELEMETRY_THRESHOLD": ("metric", "operator", "threshold"),
}
_REQUIRED_CONDITION = {
    "LOGIC_AND": ("conditions",),
    "LOGIC_OR": ("conditions",),
}
_REQUIRED_ACTION = {
    "DEVICE_COMMAND": ("device_id", "command"),
    "SEND_WEBHOOK": ("url",),
    "TRIGGER_ALERT": (),
}


def _normalize_edges(edges: list[dict[str, JsonValue]]) -> list[tuple[str, str]]:
    pairs: list[tuple[str, str]] = []
    for edge in edges:
        source = edge.get("from") or edge.get("from_node") or edge.get("source")
        target = edge.get("to") or edge.get("to_node") or edge.get("target")
        if source and target:
            pairs.append((str(source), str(target)))
    return pairs


def _detect_cycle(node_ids: set[str], edges: list[tuple[str, str]]) -> list[str] | None:
    adjacency: dict[str, list[str]] = {nid: [] for nid in node_ids}
    for source, target in edges:
        if source in adjacency:
            adjacency[source].append(target)

    visited: set[str] = set()
    stack: set[str] = set()
    path: list[str] = []

    def dfs(node: str) -> list[str] | None:
        visited.add(node)
        stack.add(node)
        path.append(node)
        for nxt in adjacency.get(node, []):
            if nxt not in visited:
                found = dfs(nxt)
                if found:
                    return found
            elif nxt in stack:
                cycle_start = path.index(nxt)
                return path[cycle_start:] + [nxt]
        path.pop()
        stack.remove(node)
        return None

    for nid in node_ids:
        if nid not in visited:
            found = dfs(nid)
            if found:
                return found
    return None


def _missing_required_config(node: dict[str, JsonValue]) -> list[str]:
    node_type = str(node.get("type", "")).upper()
    subtype = str(node.get("subtype", "")).upper()
    config = node.get("config") or {}
    missing: list[str] = []

    required: tuple[str, ...]
    if node_type == "TRIGGER":
        required = _REQUIRED_TRIGGER.get(subtype, ())
    elif node_type == "CONDITION":
        required = _REQUIRED_CONDITION.get(subtype, ())
    elif node_type == "ACTION":
        required = _REQUIRED_ACTION.get(subtype, ())
    else:
        return [f"unknown node type '{node_type}'"]

    for key in required:
        if key not in config or config[key] in (None, ""):
            missing.append(f"{subtype}.{key}")
        elif key == "conditions" and isinstance(config[key], list) and len(config[key]) == 0:
            missing.append(f"{subtype}.conditions")

    return missing


def validate_pipeline_document(
    nodes: list[dict[str, JsonValue]],
    edges: list[dict[str, JsonValue]],
) -> tuple[list[str], list[str]]:
    """Return (errors, warnings)."""
    errors: list[str] = []
    warnings: list[str] = []

    if not nodes:
        errors.append("nodes must contain at least one node")
        return errors, warnings

    node_ids: list[str] = []
    for node in nodes:
        nid = node.get("id")
        if not nid:
            errors.append("each node requires an id")
            continue
        node_ids.append(str(nid))

    if len(set(node_ids)) != len(node_ids):
        errors.append("node ids must be unique")

    node_id_set = set(node_ids)
    edge_pairs = _normalize_edges(edges)
    for source, target in edge_pairs:
        if source not in node_id_set or target not in node_id_set:
            errors.append(f"edge references unknown node: {source} -> {target}")

    cycle = _detect_cycle(node_id_set, edge_pairs)
    if cycle:
        errors.append(f"circular loop detected: {' -> '.join(cycle)}")

    triggers = [n for n in nodes if str(n.get("type", "")).upper() == "TRIGGER"]
    actions = [n for n in nodes if str(n.get("type", "")).upper() == "ACTION"]
    if not triggers:
        warnings.append("pipeline has no TRIGGER node")
    if not actions:
        warnings.append("pipeline has no ACTION node")

    for node in nodes:
        missing = _missing_required_config(node)
        for field in missing:
            errors.append(f"missing required config: {field}")

    return errors, warnings
