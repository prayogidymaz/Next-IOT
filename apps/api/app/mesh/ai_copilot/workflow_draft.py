"""Simplified workflow draft DSL produced from natural language (copilot preview)."""

from __future__ import annotations

import uuid
from enum import StrEnum
from typing import Literal

from pydantic import BaseModel, Field


class DraftTriggerKind(StrEnum):
    SENSOR_THRESHOLD = "sensor_threshold"
    CRON = "cron"
    EVENT = "event"


class DraftTrigger(BaseModel):
    kind: DraftTriggerKind
    sensor: str | None = None
    operator: Literal["lt", "lte", "gt", "gte", "eq"] | None = None
    threshold: float | None = None
    device: str | None = None
    cron: str | None = None
    event_type: str | None = None
    domain: str | None = None


class DraftAction(BaseModel):
    actuator: str | None = None
    action: str
    duration_minutes: int | None = None
    duration_seconds: int | None = None
    channels: list[str] = Field(default_factory=list)
    template: str | None = None
    webhook_url: str | None = None
    severity: str | None = None


class WorkflowDraft(BaseModel):
    draft_id: uuid.UUID
    tenant_id: uuid.UUID
    locale: str = "id"
    name: str
    description: str
    trigger: DraftTrigger
    actions: list[DraftAction]
    confidence: float = 0.85
    source: Literal["llm", "mock", "few_shot"] = "mock"
