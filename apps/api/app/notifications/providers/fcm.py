"""FCM push provider (mock unless enabled)."""

from __future__ import annotations

from app.config import settings
from app.notifications.providers.channel_base import ProviderResult
from app.types.json_types import JsonObject, as_json_str


class FcmProvider:
    channel_type = "fcm"

    async def send(
        self,
        config: JsonObject,
        title: str,
        message: str,
        severity: str,
    ) -> ProviderResult:
        token = as_json_str(config.get("fcm_token"))
        if not settings.notification_fcm_enabled or not token:
            return ProviderResult(
                success=True,
                response={"mock": True, "provider": "fcm"},
                delivered=True,
            )
        return ProviderResult(success=False, error="FCM not configured in this environment")
