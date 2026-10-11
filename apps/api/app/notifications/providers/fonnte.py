"""Fonnte WhatsApp provider."""

from __future__ import annotations

import httpx

from app.config import settings
from app.notifications.providers.channel_base import ProviderResult
from app.types.json_types import JsonObject, as_json_str


class FonnteProvider:
    channel_type = "whatsapp"

    async def send(
        self,
        config: JsonObject,
        title: str,
        message: str,
        severity: str,
    ) -> ProviderResult:
        token = as_json_str(config.get("api_token")) or settings.notification_fonnte_default_token
        target = as_json_str(config.get("phone_number"))
        if not token or not settings.notification_fonnte_enabled:
            return ProviderResult(
                success=True,
                response={"mock": True, "provider": "fonnte"},
                delivered=True,
            )
        if not target:
            return ProviderResult(success=False, error="missing phone_number in channel config")
        body_text = f"[{severity.upper()}] {title}\n{message}"
        headers = {"Authorization": token}
        payload = {"target": target, "message": body_text}
        async with httpx.AsyncClient(timeout=settings.webhook_timeout_seconds) as client:
            resp = await client.post("https://api.fonnte.com/send", headers=headers, data=payload)
        if resp.status_code >= 400:
            return ProviderResult(success=False, error=resp.text[:500])
        return ProviderResult(success=True, response={"status_code": resp.status_code}, delivered=True)
