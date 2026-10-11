"""Telegram Bot channel provider."""

from __future__ import annotations

import httpx

from app.config import settings
from app.notifications.providers.channel_base import ProviderResult
from app.types.json_types import JsonObject, as_json_str


class TelegramChannelProvider:
    channel_type = "telegram"

    async def send(
        self,
        config: JsonObject,
        title: str,
        message: str,
        severity: str,
    ) -> ProviderResult:
        bot_token = as_json_str(config.get("bot_token")) or settings.telegram_bot_token
        chat_id = as_json_str(config.get("chat_id")) or settings.default_telegram_chat_id
        if not settings.notification_telegram_enabled or not bot_token or not chat_id:
            return ProviderResult(
                success=True,
                response={"mock": True, "provider": "telegram"},
                delivered=True,
            )
        text = f"[{severity.upper()}] *{title}*\n{message}"
        url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
        async with httpx.AsyncClient(timeout=settings.webhook_timeout_seconds) as client:
            resp = await client.post(url, json={"chat_id": chat_id, "text": text, "parse_mode": "HTML"})
        if resp.status_code >= 400:
            return ProviderResult(success=False, error=resp.text[:500])
        return ProviderResult(success=True, response={"status_code": resp.status_code}, delivered=True)
