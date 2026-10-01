from typing import Literal

from pydantic import BaseModel, Field, JsonValue


class NotificationTestRequest(BaseModel):
    message: str = Field(default="Next-IOT test notification", min_length=1, max_length=500)
    channels: list[Literal["telegram", "webhook", "all"]] = Field(default=["all"])


class ProviderDispatchResult(BaseModel):
    provider: str
    success: bool
    attempts: int
    error: str | None = None


class NotificationTestResponse(BaseModel):
    alert: dict[str, JsonValue]
    results: list[ProviderDispatchResult]


class DispatchSummary(BaseModel):
    alert_event: str
    results: list[ProviderDispatchResult]
