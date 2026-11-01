"""Agent API schemas."""

from __future__ import annotations

import uuid
from datetime import datetime

from pydantic import BaseModel, Field

from app.types.json_types import JsonObject


class HealingSuggestionView(BaseModel):
    id: uuid.UUID
    workflow_id: uuid.UUID
    diagnosis_json: JsonObject
    fix_json: JsonObject
    confidence: float
    status: str
    created_at: datetime


class ChainExecutionView(BaseModel):
    id: uuid.UUID
    chain_id: str
    tenant_id: uuid.UUID
    current_step: int
    status: str
    started_at: datetime
    completed_at: datetime | None


class AlertClusterView(BaseModel):
    id: uuid.UUID
    cluster_signature: str
    alert_ids_json: list[str]
    risk_score: float
    suggested_action: str
    created_at: datetime


class ThresholdSuggestionView(BaseModel):
    id: uuid.UUID
    workflow_id: uuid.UUID
    metric: str
    old_value: float
    suggested_value: float
    reason: str
    status: str


class TriggerChainBody(BaseModel):
    event_type: str = "threshold_exceeded"
    device_id: uuid.UUID | None = None
    payload: JsonObject = Field(default_factory=dict)


class BatchExecuteBody(BaseModel):
    approve: bool = True
