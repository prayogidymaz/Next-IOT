"""Pydantic schemas for vision API."""

from __future__ import annotations

import uuid
from datetime import datetime
from enum import StrEnum

from pydantic import BaseModel, Field

from app.types.json_types import JsonObject


class PestLabel(StrEnum):
    SPODOPTERA = "spodoptera"
    APHID = "aphid"
    MITE = "mite"
    WHITEFLY = "whitefly"
    NONE = "none"


class BoundingBox(BaseModel):
    x: float
    y: float
    w: float
    h: float


class DetectionResult(BaseModel):
    bboxes: list[BoundingBox]
    labels: list[str]
    confidences: list[float]
    species_guess: str
    max_confidence: float = 0.0


class RoutingAction(StrEnum):
    AUTO_TRIGGER = "auto_trigger"
    HUMAN_REVIEW = "human_review"
    LOG_ONLY = "log_only"


class RoutingDecision(BaseModel):
    action: RoutingAction
    severity: str
    workflow_name: str | None = None
    message: str


class DetectRequest(BaseModel):
    image_base64: str = Field(min_length=16)
    device_id: uuid.UUID


class DetectResponse(BaseModel):
    detection_id: uuid.UUID
    result: DetectionResult
    routing: RoutingDecision


class FeedbackRequest(BaseModel):
    verdict: str = Field(pattern=r"^(true_positive|false_positive|species_wrong)$")
    notes: str = Field(default="", max_length=2000)


class VisionStatsResponse(BaseModel):
    tenant_id: uuid.UUID
    precision: float
    recall: float
    false_positive_rate: float
    feedback_count: int
    confidence_threshold: float


class DetectionListItem(BaseModel):
    id: uuid.UUID
    device_id: uuid.UUID
    timestamp: datetime
    labels_json: JsonObject
    max_confidence: float
    routing_action: str
    species_guess: str
