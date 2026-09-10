import hashlib
import hmac
import json
import logging
from typing import Any

import httpx

from app.config import settings
from app.notifications.formatter import build_webhook_payload
from app.notifications.providers.base import NotificationResult

logger = logging.getLogger(__name__)


def compute_webhook_signature(body: bytes, secret: str) -> str:
    digest = hmac.new(secret.encode("utf-8"), body, hashlib.sha256).hexdigest()
    return f"sha256={digest}"


class WebhookNotifier:
    name = "webhook"

    def __init__(
        self,
        *,
        url: str | None = None,
        secret: str | None = None,
        timeout_seconds: float | None = None,
        signature_header: str | None = None,
        client: httpx.AsyncClient | None = None,
    ) -> None:
        self._url = url if url is not None else settings.webhook_url
        self._secret = secret if secret is not None else settings.webhook_secret
        self._timeout = timeout_seconds if timeout_seconds is not None else settings.webhook_timeout_seconds
        self._signature_header = (
            signature_header if signature_header is not None else settings.webhook_signature_header
        )
        self._client = client

    @property
    def enabled(self) -> bool:
        return settings.webhook_enabled and bool(self._url)

    async def send(self, alert: dict[str, Any]) -> NotificationResult:
        if not self.enabled:
            return NotificationResult(
                provider=self.name,
                success=False,
                error="Webhook notifier disabled or URL not configured",
            )

        payload = build_webhook_payload(alert)
        body = json.dumps(payload, separators=(",", ":"), sort_keys=True).encode("utf-8")
        headers = {"Content-Type": "application/json"}
        if self._secret:
            headers[self._signature_header] = compute_webhook_signature(body, self._secret)

        own_client = self._client is None
        client = self._client or httpx.AsyncClient(timeout=self._timeout)
        try:
            response = await client.post(self._url, content=body, headers=headers)
            if 200 <= response.status_code < 300:
                return NotificationResult(provider=self.name, success=True)
            detail = response.text[:300]
            logger.warning("Webhook error %s: %s", response.status_code, detail)
            return NotificationResult(
                provider=self.name,
                success=False,
                error=f"Webhook HTTP {response.status_code}: {detail}",
            )
        except httpx.TimeoutException:
            return NotificationResult(provider=self.name, success=False, error="Webhook request timed out")
        except httpx.HTTPError as exc:
            return NotificationResult(provider=self.name, success=False, error=str(exc))
        finally:
            if own_client:
                await client.aclose()
