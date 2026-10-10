"""MQTT platform subscriber (aiomqtt 2.x, mocked broker)."""

from __future__ import annotations

import asyncio
import uuid
from unittest.mock import AsyncMock, MagicMock, patch

import aiomqtt
import pytest
from app.config import settings
from app.mqtt_auth.acl import MqttAclDecision
from app.mqtt_auth.schemas import MqttAuthRequest
from app.mqtt_auth.subscriber_auth import (
    SUBSCRIBER_TELEMETRY_FILTER,
    SUBSCRIBER_TELEMETRY_SHARE_FILTER,
    evaluate_platform_subscriber_acl,
    is_platform_subscriber_auth,
)
from app.mqtt_subscriber.schemas import TelemetryMqttTopic
from app.mqtt_subscriber.service import TELEMETRY_SUBSCRIBE_FILTER, MqttSubscriberService
from app.telemetry.mqtt_payload import parse_telemetry_payload_bytes
from app.types.redis_client import RedisClient
from httpx import AsyncClient
from pydantic import JsonValue

PASSWORD = "SecurePass123!"


@pytest.fixture(autouse=True)
def _enable_mqtt_subscriber_for_tests(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(settings, "mqtt_subscriber_enabled", True)


def _webhook_headers() -> dict[str, str]:
    return {"X-Internal-Secret": settings.mqtt_webhook_shared_secret}


def test_auth_allows_subscriber_user() -> None:
    auth = MqttAuthRequest(
        username=settings.mqtt_subscriber_internal_user,
        password=settings.mqtt_subscriber_internal_password,
        clientid="next-iot-subscriber-test",
    )
    assert is_platform_subscriber_auth(auth) is True


def test_auth_rejects_wrong_password() -> None:
    auth = MqttAuthRequest(
        username=settings.mqtt_subscriber_internal_user,
        password="wrong-password",
        clientid="next-iot-subscriber-test",
    )
    assert is_platform_subscriber_auth(auth) is False


def test_acl_subscriber_can_subscribe_wildcard_and_share() -> None:
    assert (
        evaluate_platform_subscriber_acl(SUBSCRIBER_TELEMETRY_FILTER, "subscribe")
        == MqttAclDecision.ALLOW
    )
    assert (
        evaluate_platform_subscriber_acl(SUBSCRIBER_TELEMETRY_SHARE_FILTER, "subscribe")
        == MqttAclDecision.ALLOW
    )


def test_acl_subscriber_cannot_publish() -> None:
    assert (
        evaluate_platform_subscriber_acl(SUBSCRIBER_TELEMETRY_FILTER, "publish")
        == MqttAclDecision.DENY
    )


@pytest.mark.asyncio
async def test_auth_endpoint_allows_subscriber_user(client: AsyncClient) -> None:
    resp = await client.post(
        "/api/v1/mqtt/auth",
        headers=_webhook_headers(),
        json={
            "username": settings.mqtt_subscriber_internal_user,
            "password": settings.mqtt_subscriber_internal_password,
            "clientid": "next-iot-subscriber-test",
        },
    )
    assert resp.status_code == 200
    assert resp.json()["result"] == "allow"


def test_subscriber_parses_topic_correctly() -> None:
    tenant_id = uuid.uuid4()
    device_id = uuid.uuid4()
    topic = f"tenants/{tenant_id}/devices/{device_id}/telemetry"
    parsed = TelemetryMqttTopic.from_mqtt_topic(topic)
    assert parsed.tenant_id == tenant_id
    assert parsed.device_id == device_id


def test_subscriber_parses_payload_json() -> None:
    raw = b'{"ts":"2026-10-09T12:00:00Z","values":{"temperature":42}}'
    payload: dict[str, JsonValue] = parse_telemetry_payload_bytes(raw)
    assert payload["values"] == {"temperature": 42}


@pytest.mark.asyncio
async def test_handle_valid_message_persists(
    client: AsyncClient,
    test_redis: RedisClient,
    unique_slug: str,
    unique_email: str,
) -> None:
    reg = await client.post(
        "/auth/register",
        json={
            "tenant_name": f"T {unique_slug}",
            "tenant_slug": unique_slug,
            "email": unique_email,
            "password": PASSWORD,
        },
    )
    token = reg.json()["tokens"]["access_token"]
    create = await client.post(
        "/api/v1/devices",
        headers={"Authorization": f"Bearer {token}"},
        json={"name": "SubPersist", "device_type": "sensor"},
    )
    device_id = create.json()["device"]["id"]
    tenant_id = create.json()["device"]["tenant_id"]
    topic = f"tenants/{tenant_id}/devices/{device_id}/telemetry"
    message = MagicMock()
    message.topic = topic
    message.payload = b'{"values":{"temperature":77}}'

    service = MqttSubscriberService(test_redis)
    with patch(
        "app.mqtt_subscriber.service.persist_telemetry_from_mqtt",
        new_callable=AsyncMock,
        return_value={"accepted_count": 1, "rejected": []},
    ) as persist_mock:
        with patch("app.mqtt_subscriber.service.async_session") as session_factory:
            session = AsyncMock()
            session_factory.return_value.__aenter__.return_value = session
            await service._handle(message)

    persist_mock.assert_awaited_once()
    session.commit.assert_awaited_once()


@pytest.mark.asyncio
async def test_handle_invalid_json_logs_and_continues() -> None:
    tenant_id = uuid.uuid4()
    device_id = uuid.uuid4()
    message = MagicMock()
    message.topic = f"tenants/{tenant_id}/devices/{device_id}/telemetry"
    message.payload = b"not-json"

    service = MqttSubscriberService(AsyncMock())
    with patch("app.mqtt_subscriber.service.persist_telemetry_from_mqtt", new_callable=AsyncMock) as persist:
        await service._handle(message)
    persist.assert_not_awaited()


@pytest.mark.asyncio
async def test_handle_topic_tenant_mismatch_rejected() -> None:
    other_tenant = uuid.uuid4()
    device_id = uuid.uuid4()
    message = MagicMock()
    message.topic = f"tenants/{other_tenant}/devices/{device_id}/telemetry"
    message.payload = b'{"values":{"temperature":1}}'

    service = MqttSubscriberService(AsyncMock())
    with patch(
        "app.mqtt_subscriber.service.persist_telemetry_from_mqtt",
        new_callable=AsyncMock,
        return_value={"accepted_count": 0, "rejected": ["device_not_found"]},
    ) as persist_mock:
        with patch("app.mqtt_subscriber.service.async_session") as session_factory:
            session = AsyncMock()
            session_factory.return_value.__aenter__.return_value = session
            await service._handle(message)

    persist_mock.assert_awaited_once()
    session.commit.assert_awaited_once()


class _EmptyMessages:
    def __aiter__(self) -> _EmptyMessages:
        return self

    async def __anext__(self) -> object:
        raise StopAsyncIteration


@pytest.mark.asyncio
async def test_client_constructed_with_aiomqtt2_kwargs() -> None:
    service = MqttSubscriberService(AsyncMock())

    class _FakeClient:
        messages = _EmptyMessages()

        async def __aenter__(self) -> _FakeClient:
            return self

        async def __aexit__(self, *_args: object) -> None:
            return None

        async def subscribe(self, *_args: object, **_kwargs: object) -> None:
            service.request_stop()

    with patch("app.mqtt_subscriber.service.aiomqtt.Client", return_value=_FakeClient()) as client_cls:
        with patch("app.mqtt_subscriber.service.asyncio.sleep", new_callable=AsyncMock):
            await asyncio.wait_for(service.run(), timeout=3.0)

    client_cls.assert_called_once()
    kwargs = client_cls.call_args.kwargs
    assert kwargs["hostname"] == settings.mqtt_broker_host
    assert kwargs["port"] == settings.mqtt_broker_port
    assert kwargs["port"] == 1883
    assert isinstance(kwargs.get("identifier"), str)
    assert str(kwargs["identifier"]).startswith("next-iot-subscriber-")


@pytest.mark.asyncio
async def test_subscriber_reconnects_on_disconnect() -> None:
    service = MqttSubscriberService(AsyncMock())
    attempts = 0

    class _FakeClient:
        messages = _EmptyMessages()

        async def __aenter__(self) -> _FakeClient:
            nonlocal attempts
            attempts += 1
            if attempts == 1:
                raise aiomqtt.MqttError("disconnect")
            service.request_stop()
            return self

        async def __aexit__(self, *_args: object) -> None:
            return None

        async def subscribe(self, *_args: object, **_kwargs: object) -> None:
            return None

    with patch("app.mqtt_subscriber.service.aiomqtt.Client", side_effect=lambda **_kw: _FakeClient()):
        await asyncio.wait_for(service.run(), timeout=5.0)

    assert attempts >= 2


@pytest.mark.asyncio
async def test_subscriber_connects_and_subscribes_share_topic() -> None:
    service = MqttSubscriberService(AsyncMock())
    subscribed: list[tuple[object, object]] = []

    class _FakeClient:
        messages = _EmptyMessages()

        async def __aenter__(self) -> _FakeClient:
            return self

        async def __aexit__(self, *_args: object) -> None:
            return None

        async def subscribe(self, topic: object, qos: object = 0) -> None:
            subscribed.append((topic, qos))
            service.request_stop()

    with patch("app.mqtt_subscriber.service.aiomqtt.Client", side_effect=lambda **_kw: _FakeClient()):
        with patch("app.mqtt_subscriber.service.logger") as log:
            await asyncio.wait_for(service.run(), timeout=3.0)
            connected = any(
                "MQTT Subscriber connected" in str(call)
                for call in log.warning.call_args_list
            )

    assert connected
    assert subscribed == [(SUBSCRIBER_TELEMETRY_SHARE_FILTER, 1)]
    assert TELEMETRY_SUBSCRIBE_FILTER == "tenants/+/devices/+/telemetry"
