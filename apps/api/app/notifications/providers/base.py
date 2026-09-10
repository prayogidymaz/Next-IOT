from dataclasses import dataclass
from typing import Any, Protocol


@dataclass
class NotificationResult:
    provider: str
    success: bool
    attempts: int = 1
    error: str | None = None


class Notifier(Protocol):
    name: str

    async def send(self, alert: dict[str, Any]) -> NotificationResult: ...
