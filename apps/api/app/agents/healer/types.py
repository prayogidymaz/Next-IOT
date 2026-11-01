"""Self-healing domain types."""

from __future__ import annotations

import uuid
from dataclasses import dataclass
from enum import StrEnum

from app.types.json_types import JsonObject


class ErrorCategory(StrEnum):
    DEVICE_OFFLINE = "device_offline"
    SCHEMA_INVALID = "schema_invalid"
    TIMEOUT = "timeout"
    PERMISSION = "permission"
    DEPENDENCY_MISSING = "dependency_missing"
    RATE_LIMITED = "rate_limited"
    UNKNOWN = "unknown"


@dataclass(frozen=True)
class BrokenWorkflow:
    workflow_id: uuid.UUID
    workflow_name: str
    failure_rate: float
    sample_size: int


@dataclass(frozen=True)
class Diagnosis:
    workflow_id: uuid.UUID
    primary_category: ErrorCategory
    error_samples: list[str]
    recommendation: str


@dataclass(frozen=True)
class FixSuggestion:
    workflow_id: uuid.UUID
    patch: JsonObject
    confidence: float
    summary: str
