import asyncio
import logging
from typing import Any

from app.config import settings
from app.notifications.providers.base import NotificationResult, Notifier
from app.notifications.providers.telegram import TelegramNotifier
from app.notifications.providers.webhook import WebhookNotifier

logger = logging.getLogger(__name__)


def build_notifiers(
    *,
    include_telegram: bool = True,
    include_webhook: bool = True,
    telegram: TelegramNotifier | None = None,
    webhook: WebhookNotifier | None = None,
) -> list[Notifier]:
    notifiers: list[Notifier] = []
    tg = telegram or TelegramNotifier()
    wh = webhook or WebhookNotifier()
    if include_telegram:
        notifiers.append(tg)
    if include_webhook:
        notifiers.append(wh)
    return notifiers


class NotificationDispatcher:
    def __init__(self, notifiers: list[Notifier] | None = None) -> None:
        self._notifiers = notifiers if notifiers is not None else build_notifiers()

    async def dispatch(self, alert: dict[str, Any]) -> list[NotificationResult]:
        results: list[NotificationResult] = []
        for notifier in self._notifiers:
            result = await self._send_with_retry(notifier, alert)
            results.append(result)
        return results

    async def _send_with_retry(self, notifier: Notifier, alert: dict[str, Any]) -> NotificationResult:
        max_retries = settings.notification_max_retries
        delay = settings.notification_retry_delay_seconds
        last_error: str | None = None

        for attempt in range(1, max_retries + 1):
            try:
                result = await asyncio.wait_for(
                    notifier.send(alert),
                    timeout=settings.webhook_timeout_seconds,
                )
                result.attempts = attempt
                if result.success:
                    return result
                last_error = result.error
            except asyncio.TimeoutError:
                last_error = f"{notifier.name} dispatch timed out"
            except Exception as exc:
                last_error = str(exc)
                logger.exception("Notifier %s failed on attempt %d", notifier.name, attempt)

            if attempt < max_retries:
                await asyncio.sleep(delay * attempt)

        logger.error(
            "Notification failed after %d attempts via %s: %s",
            max_retries,
            notifier.name,
            last_error,
        )
        return NotificationResult(
            provider=notifier.name,
            success=False,
            attempts=max_retries,
            error=last_error,
        )
