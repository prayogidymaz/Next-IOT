"""Validated MQTT telemetry topic paths for the platform subscriber."""

from __future__ import annotations

import uuid

from pydantic import BaseModel, ConfigDict, Field

from app.mqtt_auth.acl import parse_device_topic


class TelemetryMqttTopic(BaseModel):
    model_config = ConfigDict(frozen=True)

    tenant_id: uuid.UUID
    device_id: uuid.UUID
    raw_topic: str = Field(min_length=1)

    @classmethod
    def from_mqtt_topic(cls, topic: str) -> TelemetryMqttTopic:
        parsed = parse_device_topic(topic)
        if parsed is None or parsed.suffix != "telemetry":
            raise ValueError(f"Invalid telemetry topic: {topic}")
        return cls(
            tenant_id=parsed.tenant_id,
            device_id=parsed.device_id,
            raw_topic=topic.strip(),
        )
