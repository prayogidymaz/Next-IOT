"""Pydantic schemas for device attributes API."""

from __future__ import annotations

import re
import uuid
from datetime import datetime
from enum import StrEnum

from pydantic import BaseModel, ConfigDict, JsonValue, field_validator

ATTRIBUTE_KEY_PATTERN = re.compile(r"^[a-z0-9_]{1,128}$")


class AttributeScopeParam(StrEnum):
    SERVER = "server"
    SHARED = "shared"
    CLIENT = "client"


class AttributeValueBody(BaseModel):
    value: JsonValue


class DeviceAttributeItem(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    key: str
    scope: str
    value: JsonValue
    updated_at: datetime
    updated_by_user_id: uuid.UUID | None
    updated_source: str


class DeviceAttributeListResponse(BaseModel):
    items: list[DeviceAttributeItem]


class DeviceAttributePutResponse(BaseModel):
    key: str
    scope: str
    value: JsonValue
    updated_at: datetime


def validate_attribute_key(key: str) -> str:
    if not ATTRIBUTE_KEY_PATTERN.fullmatch(key):
        raise ValueError("key must match [a-z0-9_]{1,128}")
    return key


class AttributeKeyPath(BaseModel):
    key: str

    @field_validator("key")
    @classmethod
    def _key_pattern(cls, value: str) -> str:
        return validate_attribute_key(value)
