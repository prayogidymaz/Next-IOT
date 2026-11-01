"""Webhook API schemas."""

from __future__ import annotations

import uuid
from datetime import datetime

from pydantic import BaseModel, Field, HttpUrl


class WebhookCreate(BaseModel):
    url: HttpUrl
    event_types: list[str] = Field(default_factory=list)
    secret_token: str = Field(min_length=16, max_length=128)


class WebhookUpdate(BaseModel):
    url: HttpUrl | None = None
    event_types: list[str] | None = None
    active: bool | None = None


class WebhookView(BaseModel):
    id: uuid.UUID
    url: str
    event_types_json: list[str]
    active: bool
    last_delivery_at: datetime | None
    created_at: datetime

    model_config = {"from_attributes": True}
