"""Notification gateway API schemas."""

from __future__ import annotations

import uuid
from datetime import datetime
from enum import StrEnum

from pydantic import BaseModel, ConfigDict, Field, JsonValue


class ChannelTypeParam(StrEnum):
    WHATSAPP = "whatsapp"
    TELEGRAM = "telegram"
    FCM = "fcm"
    EMAIL = "email"
    SMS = "sms"


class NotificationChannelCreate(BaseModel):
    channel_type: ChannelTypeParam
    name: str = Field(min_length=1, max_length=100)
    config: dict[str, JsonValue] = Field(default_factory=dict)
    is_active: bool = True


class NotificationChannelUpdate(BaseModel):
    name: str | None = None
    config: dict[str, JsonValue] | None = None
    is_active: bool | None = None


class NotificationChannelItem(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    tenant_id: uuid.UUID
    channel_type: str
    name: str
    config: dict[str, JsonValue]
    is_active: bool
    created_at: datetime


class NotificationRuleCreate(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    alarm_filter: dict[str, JsonValue] = Field(default_factory=dict)
    channel_ids: list[uuid.UUID] = Field(min_length=1)
    throttle_seconds: int = Field(default=60, ge=1, le=86400)
    escalation_minutes: int | None = Field(default=None, ge=1, le=10080)
    is_active: bool = True


class NotificationRuleItem(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    tenant_id: uuid.UUID
    name: str
    alarm_filter: dict[str, JsonValue]
    channel_ids: list[uuid.UUID]
    throttle_seconds: int
    escalation_minutes: int | None
    is_active: bool


class NotificationLogItem(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    alarm_id: uuid.UUID | None
    channel_id: uuid.UUID | None
    channel_type: str
    status: str
    error_message: str | None
    retry_count: int
    sent_at: datetime | None
