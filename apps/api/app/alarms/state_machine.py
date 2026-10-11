"""Alarm status transitions."""

from __future__ import annotations

from app.models.alarm import AlarmStatus

ALLOWED: dict[str, frozenset[str]] = {
    AlarmStatus.ACTIVE: frozenset({AlarmStatus.ACKNOWLEDGED, AlarmStatus.CLEARED}),
    AlarmStatus.ACKNOWLEDGED: frozenset({AlarmStatus.RESOLVED, AlarmStatus.CLEARED}),
    AlarmStatus.RESOLVED: frozenset({AlarmStatus.CLEARED}),
    AlarmStatus.CLEARED: frozenset(),
}


def can_transition(current: str, target: str) -> bool:
    return target in ALLOWED.get(current, frozenset())
