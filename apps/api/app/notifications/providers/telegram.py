import logging
from typing import Any

import httpx

from app.config import settings
from app.notifications.formatter import format_telegram_html
from app.notifications.providers.base import NotificationResult

logger = logging.getLogger(__name__)


class TelegramNotifier:
    name = "telegram"

    def __init__(
        self,
        *,
        bot_token: str | None = None,
        chat_id: str | None = None,
        parse_mode: str | None = None,
        client: httpx.AsyncClient | None = None,
    ) -> None:
        self._bot_token = bot_token if bot_token is not None else settings.telegram_bot_token
        self._chat_id = chat_id if chat_id is not None else settings.default_telegram_chat_id
        self._parse_mode = parse_mode if parse_mode is not None else settings.telegram_parse_mode
        self._client = client

    @property
    def enabled(self) -> bool:
        return settings.telegram_enabled and bool(self._bot_token) and bool(self._chat_id)

    async def send(self, alert: dict[str, Any]) -> NotificationResult:
        if not self.enabled:
            return NotificationResult(
                provider=self.name,
                success=False,
                error="Telegram notifier disabled or not configured",
            )

        text = format_telegram_html(alert)
        url = f"https://api.telegram.org/bot{self._bot_token}/sendMessage"
        payload = {
            "chat_id": self._chat_id,
            "text": text,
            "parse_mode": self._parse_mode,
            "disable_web_page_preview": True,
        }

        own_client = self._client is None
        client = self._client or httpx.AsyncClient(timeout=settings.webhook_timeout_seconds)
        try:
            response = await client.post(url, json=payload)
            if response.status_code == 200 and response.json().get("ok"):
                return NotificationResult(provider=self.name, success=True)
            detail = response.text[:300]
            logger.warning("Telegram API error %s: %s", response.status_code, detail)
            return NotificationResult(
                provider=self.name,
                success=False,
                error=f"Telegram API {response.status_code}: {detail}",
            )
        except httpx.TimeoutException:
            return NotificationResult(provider=self.name, success=False, error="Telegram request timed out")
        except httpx.HTTPError as exc:
            return NotificationResult(provider=self.name, success=False, error=str(exc))
        finally:
            if own_client:
                await client.aclose()
