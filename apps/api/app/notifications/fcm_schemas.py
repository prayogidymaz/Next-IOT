"""Schemas for FCM token registration API."""

from __future__ import annotations

import uuid
from datetime import datetime

from pydantic import BaseModel, Field


class FcmRegisterRequest(BaseModel):
    token: str = Field(min_length=8, max_length=512)
    device_type: str = Field(default="mobile", max_length=64)


class FcmTokenView(BaseModel):
    id: uuid.UUID
    token: str
    device_type: str
    last_seen_at: datetime
    created_at: datetime
