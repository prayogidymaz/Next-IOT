"""Match mesh events and payloads to workflow triggers."""

from __future__ import annotations

from datetime import UTC, datetime, time

from app.mesh.schemas import MeshEvent
from app.mesh.workflow_schema import MeshWorkflowDefinition, WorkflowTriggerType
from app.types.json_types import JsonObject, JsonValue


def _compare_op(actual: JsonValue, expected: JsonValue) -> bool:
    if isinstance(expected, dict):
        for op, bound in expected.items():
            if op == "$gte":
                if not isinstance(actual, int | float) or not isinstance(bound, int | float):
                    return False
                if float(actual) < float(bound):
                    return False
            elif op == "$lte":
                if not isinstance(actual, int | float) or not isinstance(bound, int | float):
                    return False
                if float(actual) > float(bound):
                    return False
            elif op == "$eq":
                if actual != bound:
                    return False
            else:
                return False
        return True
    return actual == expected


def _match_threshold_rule(actual: JsonObject, pattern: JsonObject) -> bool:
    metric_name = pattern.get("metric")
    operator = pattern.get("operator")
    threshold_raw = pattern.get("threshold")
    if not isinstance(metric_name, str) or not isinstance(operator, str):
        return True
    if not isinstance(threshold_raw, int | float):
        return False
    reading = actual.get(metric_name)
    if reading is None and isinstance(actual.get("metrics"), dict):
        metrics = actual.get("metrics")
        if isinstance(metrics, dict):
            nested = metrics.get(metric_name)
            if isinstance(nested, int | float):
                reading = nested
    if not isinstance(reading, int | float):
        return False
    value = float(reading)
    bound = float(threshold_raw)
    if operator == "lt":
        return value < bound
    if operator == "gt":
        return value > bound
    if operator == "lte":
        return value <= bound
    if operator == "gte":
        return value >= bound
    return False


def _match_object(actual: JsonObject, pattern: JsonObject) -> bool:
    if "metric" in pattern and "operator" in pattern and "threshold" in pattern:
        if not _match_threshold_rule(actual, pattern):
            return False
    for key, expected in pattern.items():
        if key in {"metric", "operator", "threshold"}:
            continue
        actual_value = actual.get(key)
        if not _compare_op(actual_value, expected):
            return False
    return True


def _in_time_window(now: datetime, time_filter: JsonObject) -> bool:
    start_raw = time_filter.get("start")
    end_raw = time_filter.get("end")
    if not isinstance(start_raw, str) or not isinstance(end_raw, str):
        return True
    try:
        start_parts = [int(p) for p in start_raw.split(":")]
        end_parts = [int(p) for p in end_raw.split(":")]
        start_t = time(start_parts[0], start_parts[1] if len(start_parts) > 1 else 0)
        end_t = time(end_parts[0], end_parts[1] if len(end_parts) > 1 else 0)
    except (ValueError, IndexError):
        return True
    local = now.astimezone(UTC).time()
    if start_t <= end_t:
        return start_t <= local <= end_t
    return local >= start_t or local <= end_t


def workflow_matches_event(definition: MeshWorkflowDefinition, event: MeshEvent) -> bool:
    trigger = definition.trigger
    if trigger.type != WorkflowTriggerType.MESH_EVENT:
        return False
    filt = trigger.filter
    if filt is None:
        return True
    if filt.domain is not None and filt.domain != event.domain.value:
        return False
    if filt.event_type is not None and filt.event_type != event.event_type:
        return False
    payload_obj: JsonObject = dict(event.payload)
    if filt.payload_match is not None and not _match_object(payload_obj, filt.payload_match):
        return False
    ctx_obj: JsonObject = {
        "farm_id": str(event.context.farm_id) if event.context.farm_id else None,
        "plot_id": str(event.context.plot_id) if event.context.plot_id else None,
        "physical_zone": event.context.physical_zone,
    }
    if filt.context_match is not None and not _match_object(ctx_obj, filt.context_match):
        return False
    if filt.time_filter is not None and not _in_time_window(event.timestamp, filt.time_filter):
        return False
    return True
