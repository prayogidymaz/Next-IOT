"""aiomqtt 2.x subscriber — forwards broker telemetry into the API ingest pipeline."""

from __future__ import annotations

import asyncio
import logging
import os
import socket

import aiomqtt
from pydantic import JsonValue

from app.config import settings
from app.database import async_session
from app.mqtt_auth.subscriber_auth import SUBSCRIBER_TELEMETRY_SHARE_FILTER
from app.mqtt_subscriber.schemas import TelemetryMqttTopic
from app.mqtt_subscriber.telemetry_ingest import persist_telemetry_from_mqtt
from app.telemetry.mqtt_payload import parse_telemetry_payload_bytes
from app.types.redis_client import RedisClient

logger = logging.getLogger(__name__)

TELEMETRY_SUBSCRIBE_FILTER = "tenants/+/devices/+/telemetry"


def _mqtt_client_identifier() -> str:
    return f"next-iot-subscriber-{socket.gethostname()}-{os.getpid()}"


def _message_payload_bytes(payload: object) -> bytes | None:
    if isinstance(payload, bytes):
        return payload
    if isinstance(payload, bytearray):
        return bytes(payload)
    if isinstance(payload, str):
        return payload.encode("utf-8")
    return None


class MqttSubscriberService:
    def __init__(self, redis: RedisClient) -> None:
        self._redis = redis
        self._stopping = False

    def request_stop(self) -> None:
        self._stopping = True

    async def _handle(self, message: aiomqtt.Message) -> None:
        topic_str = str(message.topic)
        try:
            parsed_topic = TelemetryMqttTopic.from_mqtt_topic(topic_str)
        except ValueError:
            logger.warning("MQTT Subscriber ignored topic: %s", topic_str)
            return

        payload_bytes = _message_payload_bytes(message.payload)
        if payload_bytes is None:
            logger.warning("MQTT Subscriber non-bytes payload on %s", topic_str)
            return

        try:
            payload_obj: dict[str, JsonValue] = parse_telemetry_payload_bytes(payload_bytes)
        except Exception as exc:
            logger.warning("MQTT Subscriber invalid payload on %s: %s", topic_str, exc)
            return

        if not payload_obj:
            logger.warning("MQTT Subscriber empty payload on %s", topic_str)
            return

        values = payload_obj.get("values")
        temp_log = values.get("temperature") if isinstance(values, dict) else None
        logger.warning(
            "Telemetry received: tenant=%s device=%s temp=%s",
            parsed_topic.tenant_id,
            parsed_topic.device_id,
            temp_log,
        )

        async with async_session() as db:
            try:
                result = await persist_telemetry_from_mqtt(
                    db,
                    self._redis,
                    topic=parsed_topic,
                    payload_obj=payload_obj,
                    client_id=_mqtt_client_identifier(),
                )
                await db.commit()
            except Exception:
                await db.rollback()
                logger.exception("MQTT Subscriber persist failed on %s", topic_str)
                return

        logger.warning(
            "MQTT Subscriber persisted: device=%s accepted=%s rejected=%s",
            parsed_topic.device_id,
            result.get("accepted_count", 0),
            result.get("rejected", []),
        )

    async def run(self) -> None:
        # Defer first connect until HTTP server accepts EMQX auth/ACL webhooks (same event loop).
        await asyncio.sleep(1.0)
        backoff = 1.0
        max_backoff = min(settings.mqtt_subscriber_reconnect_max_seconds, 30.0)
        while not self._stopping:
            try:
                async with aiomqtt.Client(
                    hostname=settings.mqtt_broker_host,
                    port=settings.mqtt_broker_port,
                    username=settings.mqtt_subscriber_internal_user,
                    password=settings.mqtt_subscriber_internal_password,
                    identifier=_mqtt_client_identifier(),
                    keepalive=30,
                ) as client:
                    await client.subscribe(SUBSCRIBER_TELEMETRY_SHARE_FILTER, qos=1)
                    logger.warning(
                        "MQTT Subscriber connected; Subscribed to %s",
                        TELEMETRY_SUBSCRIBE_FILTER,
                    )
                    backoff = 1.0
                    async for message in client.messages:
                        if self._stopping:
                            break
                        try:
                            await self._handle(message)
                        except Exception:
                            logger.exception("MQTT Subscriber message handler error")
            except aiomqtt.MqttError as exc:
                logger.warning(
                    "MQTT Subscriber disconnected: %s (retry in %.1fs)",
                    exc,
                    backoff,
                )
            except Exception:
                logger.exception("MQTT Subscriber unexpected error (retry in %.1fs)", backoff)

            if self._stopping:
                break
            await asyncio.sleep(backoff)
            backoff = min(backoff * 2.0, max_backoff)

        logger.warning("MQTT Subscriber stopped")
