"""Reporting API schemas."""

from __future__ import annotations

import uuid
from datetime import datetime

from pydantic import BaseModel, Field


class ReportTemplateCreate(BaseModel):
    name: str = Field(min_length=1, max_length=255)
    description: str = ""
    config_json: dict[str, object] = Field(default_factory=dict)
    is_public: bool = False


class ReportTemplateUpdate(BaseModel):
    name: str | None = None
    description: str | None = None
    config_json: dict[str, object] | None = None
    is_public: bool | None = None


class ReportTemplateView(BaseModel):
    id: uuid.UUID
    tenant_id: uuid.UUID
    name: str
    description: str
    config_json: dict[str, object]
    is_public: bool
    created_at: datetime

    model_config = {"from_attributes": True}


class ReportScheduleCreate(BaseModel):
    cron_expression: str
    recipients: list[str] = Field(default_factory=list)
    format: str = Field(pattern=r"^(pdf|csv|excel)$")
    enabled: bool = True


class ReportScheduleView(BaseModel):
    id: uuid.UUID
    template_id: uuid.UUID
    cron_expression: str
    recipients_json: list[str]
    format: str
    enabled: bool

    model_config = {"from_attributes": True}


class ReportGenerationView(BaseModel):
    id: uuid.UUID
    template_id: uuid.UUID
    generated_at: datetime
    status: str
    file_url: str | None

    model_config = {"from_attributes": True}
