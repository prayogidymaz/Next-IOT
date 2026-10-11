"""Alarm API schemas."""

from __future__ import annotations

import uuid
from datetime import datetime
from enum import StrEnum

from pydantic import BaseModel, ConfigDict, Field, JsonValue


class AlarmSeverityParam(StrEnum):
    CRITICAL = "critical"
    MAJOR = "major"
    MINOR = "minor"
    WARNING = "warning"
    INFO = "info"


class AlarmStatusParam(StrEnum):
    ACTIVE = "active"
    ACKNOWLEDGED = "acknowledged"
    RESOLVED = "resolved"
    CLEARED = "cleared"


class AlarmCreateRequest(BaseModel):
    device_id: uuid.UUID | None = None
    alarm_type: str = Field(min_length=1, max_length=64)
    severity: AlarmSeverityParam
    title: str = Field(min_length=1, max_length=200)
    message: str | None = None
    details: dict[str, JsonValue] = Field(default_factory=dict)
    source: str = Field(default="manual", max_length=32)


class AlarmNoteRequest(BaseModel):
    note: str | None = None


class AlarmCommentRequest(BaseModel):
    note: str = Field(min_length=1)


class AlarmHistoryItem(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    action: str
    actor_user_id: uuid.UUID | None
    note: str | None
    occurred_at: datetime


class AlarmItem(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    tenant_id: uuid.UUID
    device_id: uuid.UUID | None
    alarm_type: str
    severity: str
    status: str
    title: str
    message: str | None
    details: dict[str, JsonValue]
    source: str
    rule_id: uuid.UUID | None
    fingerprint: str
    occurred_at: datetime
    acknowledged_at: datetime | None
    acknowledged_by_user_id: uuid.UUID | None
    resolved_at: datetime | None
    resolved_by_user_id: uuid.UUID | None
    cleared_at: datetime | None
    escalation_count: int


class AlarmListResponse(BaseModel):
    items: list[AlarmItem]
    total: int


class AlarmHistoryResponse(BaseModel):
    items: list[AlarmHistoryItem]
