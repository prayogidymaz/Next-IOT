"""Parse plan limit JSON into typed helpers."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class PlanLimits:
    max_devices: int | None
    max_users: int | None
    max_rules: int | None
    max_dashboards: int | None
    max_api_calls_per_day: int | None
    max_messages_per_month: int | None
    data_retention_days: int
    features: frozenset[str]


def _int_or_none(value: object) -> int | None:
    if value is None:
        return None
    if isinstance(value, bool):
        return None
    if isinstance(value, int):
        return value
    return None


def parse_plan_limits(raw: dict[str, object]) -> PlanLimits:
    features_raw = raw.get("features")
    features: frozenset[str] = frozenset()
    if isinstance(features_raw, list):
        names: list[str] = []
        for item in features_raw:
            if isinstance(item, str):
                names.append(item)
        features = frozenset(names)
    retention = _int_or_none(raw.get("data_retention_days"))
    return PlanLimits(
        max_devices=_int_or_none(raw.get("max_devices")),
        max_users=_int_or_none(raw.get("max_users")),
        max_rules=_int_or_none(raw.get("max_rules")),
        max_dashboards=_int_or_none(raw.get("max_dashboards")),
        max_api_calls_per_day=_int_or_none(raw.get("max_api_calls_per_day")),
        max_messages_per_month=_int_or_none(raw.get("max_messages_per_month")),
        data_retention_days=retention if retention is not None else 7,
        features=features,
    )
