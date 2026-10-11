"""Twilio SMS provider (mock unless configured)."""

from __future__ import annotations

import httpx

from app.config import settings
from app.notifications.providers.channel_base import ProviderResult
from app.types.json_types import JsonObject, as_json_str


class TwilioSmsProvider:
    channel_type = "sms"

    async def send(
        self,
        config: JsonObject,
        title: str,
        message: str,
        severity: str,
    ) -> ProviderResult:
        phone = as_json_str(config.get("phone_number"))
        if not phone:
            return ProviderResult(success=False, error="missing phone_number")
        if not settings.notification_twilio_account_sid:
            return ProviderResult(
                success=True,
                response={"mock": True, "provider": "sms", "to": phone},
                delivered=True,
            )
        url = (
            f"https://api.twilio.com/2010-04-01/Accounts/"
            f"{settings.notification_twilio_account_sid}/Messages.json"
        )
        auth = (settings.notification_twilio_account_sid, settings.notification_twilio_auth_token)
        data = {
            "To": phone,
            "From": settings.notification_twilio_from_number,
            "Body": f"[{severity}] {title}: {message}",
        }
        async with httpx.AsyncClient(timeout=settings.webhook_timeout_seconds) as client:
            resp = await client.post(url, data=data, auth=auth)
        if resp.status_code >= 400:
            return ProviderResult(success=False, error=resp.text[:500])
        return ProviderResult(success=True, response={"status_code": resp.status_code}, delivered=True)
