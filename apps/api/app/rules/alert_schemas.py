from datetime import datetime
from typing import Any, Literal

from pydantic import BaseModel, Field


class AlertResponse(BaseModel):
    id: str
    event: str
    rule_id: str | None = None
    device_id: str
    tenant_id: str
    metric: str | None = None
    operator: str | None = None
    threshold: float | None = None
    actual_value: float | None = None
    action_type: str | None = None
    notification_channel: str | None = None
    reading_id: str | None = None
    severity: Literal["critical", "warning", "info"] = "info"
    status: Literal["active", "resolved"] = "active"
    timestamp: str | None = None


class AlertListResponse(BaseModel):
    count: int
    items: list[AlertResponse]


class AlertSummaryResponse(BaseModel):
    active_count: int
    items: list[AlertResponse] = Field(default_factory=list)
