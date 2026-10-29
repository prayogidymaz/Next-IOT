"""Marketplace API schemas."""

from __future__ import annotations

import uuid
from datetime import datetime

from pydantic import BaseModel, Field

from app.types.json_types import JsonObject


class WorkflowTemplateView(BaseModel):
    id: uuid.UUID
    name: str
    description: str
    category: str
    tags_json: list[str]
    author_tenant_id: uuid.UUID
    snapshot_json: JsonObject
    downloads_count: int
    rating_avg: float
    rating_count: int
    published: bool
    created_at: datetime
    locale: str


class PublishTemplateBody(BaseModel):
    workflow_id: uuid.UUID
    name: str
    description: str = ""
    category: str
    tags: list[str] = Field(default_factory=list)
    locale: str = "id"


class RateTemplateBody(BaseModel):
    rating: int = Field(ge=1, le=5)
    review: str = ""


class DownloadTemplateBody(BaseModel):
    target_tenant_id: uuid.UUID | None = None
