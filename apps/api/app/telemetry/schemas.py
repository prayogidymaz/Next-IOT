import uuid
from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field, field_validator


class TelemetryIngestRequest(BaseModel):
    timestamp: datetime = Field(description="ISO-8601 timestamp when sensor data was recorded")
    metrics: dict[str, float | int] = Field(min_length=1, description="Sensor readings e.g. temperature, humidity")

    @field_validator("metrics")
    @classmethod
    def validate_metrics(cls, value: dict[str, float | int]) -> dict[str, float | int]:
        for key in value:
            normalized = key.replace("_", "").replace(".", "")
            if not normalized.isalnum():
                raise ValueError(f"Invalid metric key: {key}")
        return value


class TelemetryIngestResponse(BaseModel):
    reading_id: uuid.UUID
    device_id: uuid.UUID
    tenant_id: uuid.UUID
    recorded_at: datetime
    metrics: dict[str, Any]
    cached: bool = True
    rules_triggered: int = 0


class TelemetryLatestResponse(BaseModel):
    device_id: uuid.UUID
    reading_id: str | None = None
    recorded_at: str | None = None
    metrics: dict[str, Any]
    cached_at: str | None = None
    source: str = "redis"


class TelemetryHistoryItem(BaseModel):
    reading_id: uuid.UUID
    recorded_at: datetime
    metrics: dict[str, Any]
    ingested_at: datetime


class TelemetryHistoryResponse(BaseModel):
    device_id: uuid.UUID
    count: int
    items: list[TelemetryHistoryItem]
