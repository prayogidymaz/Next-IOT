"""Long-lived aiomqtt client for internal publishes."""

from __future__ import annotations

import asyncio
import json
import logging
import os
import socket
from dataclasses import dataclass

import aiomqtt
from pydantic import JsonValue

from app.config import settings

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class _PublishJob:
    topic: str
    payload: bytes
    qos: int


def _publisher_client_identifier() -> str:
    return f"next-iot-publisher-{socket.gethostname()}-{os.getpid()}"


class MqttPublisherService:
    def __init__(self) -> None:
        self._queue: asyncio.Queue[_PublishJob | None] = asyncio.Queue()
        self._stopping = False

    def request_stop(self) -> None:
        self._stopping = True
        self._queue.put_nowait(None)

    async def publish_json(self, topic: str, payload: dict[str, JsonValue], qos: int = 1) -> None:
        body = json.dumps(payload, separators=(",", ":"), ensure_ascii=False).encode("utf-8")
        await self._queue.put(_PublishJob(topic=topic, payload=body, qos=qos))

    async def run(self) -> None:
        await asyncio.sleep(1.0)
        backoff = 1.0
        max_backoff = min(settings.mqtt_subscriber_reconnect_max_seconds, 30.0)
        while not self._stopping:
            try:
                async with aiomqtt.Client(
                    hostname=settings.mqtt_broker_host,
                    port=settings.mqtt_broker_port,
                    username=settings.mqtt_publisher_internal_user,
                    password=settings.mqtt_publisher_internal_password,
                    identifier=_publisher_client_identifier(),
                    keepalive=30,
                ) as client:
                    logger.warning("MQTT Publisher connected")
                    backoff = 1.0
                    while not self._stopping:
                        job = await self._queue.get()
                        if job is None:
                            break
                        await client.publish(job.topic, job.payload, qos=job.qos)
            except aiomqtt.MqttError as exc:
                logger.warning("MQTT Publisher disconnected: %s (retry in %.1fs)", exc, backoff)
            except Exception:
                logger.exception("MQTT Publisher unexpected error (retry in %.1fs)", backoff)

            if self._stopping:
                break
            await asyncio.sleep(backoff)
            backoff = min(backoff * 2.0, max_backoff)
        logger.warning("MQTT Publisher stopped")
