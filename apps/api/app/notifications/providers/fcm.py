"""FCM push provider (gateway channel adapter)."""

from __future__ import annotations

from app.config import settings
from app.notifications.fcm_push import get_fcm_push_client
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
        if not token:
            return ProviderResult(success=False, error="missing fcm_token")
        client = get_fcm_push_client()
        result = await client.send(
            token,
            title=title,
            body=message,
            data={"severity": severity},
        )
        if result.success:
            return ProviderResult(success=True, delivered=True, response={"provider": "fcm"})
        if not settings.notification_fcm_enabled:
            return ProviderResult(success=True, delivered=True, response={"mock": True, "provider": "fcm"})
        return ProviderResult(success=False, error=result.error or "fcm send failed")
