"""Smart Home & Building telemetry metric validation."""

from __future__ import annotations

from pydantic import JsonValue

SMART_HOME_METRIC_KEYS = frozenset(
    {"relay_state", "pir_motion", "hvac_temp", "lock_state"},
)

RelayState = str
LockState = str


def _normalize_relay_state(value: JsonValue) -> RelayState:
    if isinstance(value, str):
        upper = value.strip().upper()
        if upper in {"ON", "OFF"}:
            return upper
    if value in (1, 1.0, True):
        return "ON"
    if value in (0, 0.0, False):
        return "OFF"
    raise ValueError("relay_state must be ON or OFF")


def _normalize_pir_motion(value: JsonValue) -> bool:
    if isinstance(value, bool):
        return value
    if isinstance(value, (int, float)):
        return bool(value)
    if isinstance(value, str):
        normalized = value.strip().lower()
        if normalized in {"true", "1", "yes", "motion", "detected"}:
            return True
        if normalized in {"false", "0", "no", "clear", "idle"}:
            return False
    raise ValueError("pir_motion must be a boolean")


def _normalize_hvac_temp(value: JsonValue) -> float:
    try:
        return float(value)
    except (TypeError, ValueError) as exc:
        raise ValueError("hvac_temp must be numeric") from exc


def _normalize_lock_state(value: JsonValue) -> LockState:
    if isinstance(value, str):
        upper = value.strip().upper()
        if upper in {"LOCKED", "UNLOCKED"}:
            return upper
    raise ValueError("lock_state must be LOCKED or UNLOCKED")


def normalize_smart_home_metric(key: str, value: JsonValue) -> JsonValue:
    if key == "relay_state":
        return _normalize_relay_state(value)
    if key == "pir_motion":
        return _normalize_pir_motion(value)
    if key == "hvac_temp":
        return _normalize_hvac_temp(value)
    if key == "lock_state":
        return _normalize_lock_state(value)
    return value


def normalize_telemetry_metrics(metrics: dict[str, JsonValue]) -> dict[str, JsonValue]:
    normalized: dict[str, JsonValue] = {}
    for key, value in metrics.items():
        if key in SMART_HOME_METRIC_KEYS:
            normalized[key] = normalize_smart_home_metric(key, value)
            continue
        if isinstance(value, bool):
            normalized[key] = value
            continue
        if isinstance(value, str):
            normalized[key] = value
            continue
        if isinstance(value, int):
            normalized[key] = float(value)
            continue
        if isinstance(value, float):
            normalized[key] = value
            continue
        raise ValueError(f"Unsupported metric value type for key '{key}'")
    return normalized
