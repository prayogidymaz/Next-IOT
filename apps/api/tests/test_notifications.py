import json
from datetime import UTC, datetime
from unittest.mock import AsyncMock, MagicMock, patch

import httpx
import pytest
import redis.asyncio as aioredis
from httpx import AsyncClient

from app.config import settings
from app.notifications.dispatcher import NotificationDispatcher
from app.notifications.formatter import build_webhook_payload, format_telegram_html
from app.notifications.providers.base import NotificationResult
from app.notifications.providers.telegram import TelegramNotifier
from app.notifications.providers.webhook import WebhookNotifier, compute_webhook_signature
from app.notifications.worker import process_alert_queue_once
from app.rules.alerts import ALERTS_QUEUE, emit_alert

PASSWORD = "SecurePass123!"

SAMPLE_ALERT = {
    "event": "rule.triggered",
    "rule_id": "r1",
    "device_id": "d1",
    "tenant_id": "t1",
    "metric": "temperature",
    "operator": "gt",
    "threshold": 25.0,
    "actual_value": 30.0,
    "action_type": "alert",
    "reading_id": "rd1",
    "timestamp": "2026-09-10T10:00:00+00:00",
}


def test_telegram_notifier_reads_settings_from_environment():
    """TelegramNotifier must use Settings (loaded from .env via pydantic-settings)."""
    notifier = TelegramNotifier()
    assert notifier._bot_token == settings.telegram_bot_token
    assert notifier._chat_id == settings.default_telegram_chat_id
    assert notifier._parse_mode == settings.telegram_parse_mode


def test_format_telegram_html_escapes_and_includes_fields():
    text = format_telegram_html(SAMPLE_ALERT)
    assert "<b>Next-IOT Alert</b>" in text
    assert "temperature" in text
    assert "30.0" in text
    assert "gt" in text


def test_build_webhook_payload_structure():
    payload = build_webhook_payload(SAMPLE_ALERT)
    assert payload["source"] == "next-iot"
    assert payload["event"] == "rule.triggered"
    assert payload["actual_value"] == 30.0


def test_compute_webhook_signature():
    body = b'{"event":"test"}'
    sig = compute_webhook_signature(body, "secret-key")
    assert sig.startswith("sha256=")
    assert len(sig) > 20


@pytest.mark.asyncio
async def test_webhook_notifier_sends_signed_payload():
    captured: dict = {}

    async def handler(request: httpx.Request) -> httpx.Response:
        captured["headers"] = dict(request.headers)
        captured["body"] = request.content
        return httpx.Response(200, json={"ok": True})

    transport = httpx.MockTransport(handler)
    client = httpx.AsyncClient(transport=transport)

    notifier = WebhookNotifier(
        url="https://hooks.example.com/alerts",
        secret="test-secret",
        client=client,
    )

    with patch.object(settings, "webhook_enabled", True):
        result = await notifier.send(SAMPLE_ALERT)

    assert result.success is True
    header_key = settings.webhook_signature_header.lower()
    assert header_key in captured["headers"]
    expected_sig = compute_webhook_signature(captured["body"], "test-secret")
    assert captured["headers"][header_key] == expected_sig


@pytest.mark.asyncio
async def test_telegram_notifier_formats_html_message():
    captured: dict = {}

    async def handler(request: httpx.Request) -> httpx.Response:
        captured["json"] = json.loads(request.content)
        return httpx.Response(200, json={"ok": True})

    transport = httpx.MockTransport(handler)
    client = httpx.AsyncClient(transport=transport)

    notifier = TelegramNotifier(
        bot_token="123:ABC",
        chat_id="-100123",
        client=client,
    )

    with patch.object(settings, "telegram_enabled", True):
        result = await notifier.send(SAMPLE_ALERT)

    assert result.success is True
    assert captured["json"]["parse_mode"] == "HTML"
    assert "temperature" in captured["json"]["text"]


@pytest.mark.asyncio
async def test_dispatcher_retries_on_failure():
    attempts = 0

    class FailingNotifier:
        name = "mock"

        async def send(self, alert):
            nonlocal attempts
            attempts += 1
            return NotificationResult(provider=self.name, success=False, error="boom")

    with patch.object(settings, "notification_max_retries", 3):
        with patch.object(settings, "notification_retry_delay_seconds", 0):
            dispatcher = NotificationDispatcher(notifiers=[FailingNotifier()])
            results = await dispatcher.dispatch(SAMPLE_ALERT)

    assert attempts == 3
    assert results[0].success is False
    assert results[0].attempts == 3


@pytest.mark.asyncio
async def test_worker_consumes_alert_from_queue():
    redis = aioredis.from_url(settings.redis_url, decode_responses=True)
    await redis.delete(ALERTS_QUEUE, "device:alerts:history")

    mock_notifier = AsyncMock()
    mock_notifier.name = "mock"
    mock_notifier.send.return_value = NotificationResult(provider="mock", success=True)

    await emit_alert(
        redis,
        rule_id="r1",
        device_id="d1",
        tenant_id="t1",
        metric="temperature",
        operator="gt",
        threshold=25.0,
        actual_value=30.0,
        action_type="alert",
        reading_id="rd1",
    )

    dispatcher = NotificationDispatcher(notifiers=[mock_notifier])
    processed = await process_alert_queue_once(redis, dispatcher)

    assert processed == 1
    mock_notifier.send.assert_awaited_once()
    assert await redis.rpop(ALERTS_QUEUE) is None
    await redis.aclose()


@pytest.mark.asyncio
async def test_notifications_test_endpoint(client: AsyncClient, unique_slug: str, unique_email: str):
    reg = await client.post(
        "/auth/register",
        json={
            "tenant_name": "Notify Co",
            "tenant_slug": unique_slug,
            "email": unique_email,
            "password": PASSWORD,
        },
    )
    token = reg.json()["tokens"]["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    with patch(
        "app.notifications.router.NotificationDispatcher.dispatch",
        new_callable=AsyncMock,
    ) as mock_dispatch:
        mock_dispatch.return_value = [
            NotificationResult(provider="telegram", success=False, error="not configured"),
            NotificationResult(provider="webhook", success=False, error="not configured"),
        ]
        resp = await client.post(
            "/api/v1/notifications/test",
            headers=headers,
            json={"message": "Hello from test", "channels": ["all"]},
        )

    assert resp.status_code == 200
    body = resp.json()
    assert body["alert"]["event"] == "notification.test"
    assert body["alert"]["message"] == "Hello from test"
    assert len(body["results"]) == 2
    mock_dispatch.assert_awaited_once()
