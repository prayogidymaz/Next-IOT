"""Telemetry persist payload for post-commit rule execution."""

from __future__ import annotations

import uuid
from dataclasses import dataclass
from datetime import datetime

from pydantic import JsonValue


@dataclass(frozen=True)
class TelemetryRuleEvent:
    tenant_id: uuid.UUID
    device_id: uuid.UUID
    metrics: dict[str, JsonValue]
    recorded_at: datetime
    reading_id: uuid.UUID
