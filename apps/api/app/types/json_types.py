"""JSON-safe types for API payloads (strict JsonValue / JsonObject only)."""

from pydantic import JsonValue

JsonObject = dict[str, JsonValue]
JsonArray = list[JsonValue]


def as_json_str(value: JsonValue | None) -> str | None:
    return value if isinstance(value, str) else None


def as_json_object(value: JsonValue | None) -> JsonObject | None:
    if isinstance(value, dict):
        return value
    return None


def json_value_to_float(value: JsonValue | None) -> float | None:
    if isinstance(value, bool) or value is None:
        return None
    if isinstance(value, int | float):
        return float(value)
    if isinstance(value, str):
        try:
            return float(value)
        except ValueError:
            return None
    return None


def numeric_metrics(metrics: dict[str, JsonValue]) -> dict[str, float]:
    parsed: dict[str, float] = {}
    for key, value in metrics.items():
        number = json_value_to_float(value)
        if number is not None:
            parsed[key] = number
    return parsed


def metric_float(metrics: dict[str, JsonValue], *keys: str) -> float | None:
    for key in keys:
        if key not in metrics:
            continue
        parsed = json_value_to_float(metrics[key])
        if parsed is not None:
            return parsed
    return None


__all__ = [
    "JsonArray",
    "JsonObject",
    "JsonValue",
    "as_json_object",
    "as_json_str",
    "json_value_to_float",
    "metric_float",
    "numeric_metrics",
]
