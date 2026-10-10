"""MQTT publisher interface for internal platform publishes."""

from __future__ import annotations

from typing import Protocol

from pydantic import JsonValue


class MqttPublisherProtocol(Protocol):
    async def publish_json(self, topic: str, payload: dict[str, JsonValue], qos: int = 1) -> None: ...
