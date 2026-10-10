"""No-op MQTT publisher when publishing is disabled."""

from __future__ import annotations

from pydantic import JsonValue


class NoopMqttPublisher:
    async def publish_json(self, topic: str, payload: dict[str, JsonValue], qos: int = 1) -> None:
        return None
