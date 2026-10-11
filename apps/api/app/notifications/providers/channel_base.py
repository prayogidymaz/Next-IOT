"""Channel provider interface for notification gateway."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol

from app.types.json_types import JsonObject


@dataclass(frozen=True)
class ProviderResult:
    success: bool
    response: JsonObject | None = None
    error: str | None = None
    delivered: bool = False


class ChannelProvider(Protocol):
    channel_type: str

    async def send(
        self,
        config: JsonObject,
        title: str,
        message: str,
        severity: str,
    ) -> ProviderResult: ...
