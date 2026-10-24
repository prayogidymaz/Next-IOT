"""Shared helpers for mesh device simulators."""

from __future__ import annotations

import json
import os
import uuid
from dataclasses import dataclass
from datetime import UTC, datetime
from typing import Protocol

import aiomqtt
from app.mesh.event_bus import MeshDomain, mesh_event_topic
from pydantic import JsonValue


@dataclass(frozen=True)
class SimulatorEnv:
    tenant_id: uuid.UUID
    device_id: uuid.UUID
    mqtt_broker: str
    mqtt_port: int
    mqtt_username: str
    mqtt_password: str
    emit_interval_seconds: float
    http_port: int

    @classmethod
    def from_os(cls) -> SimulatorEnv:
        tenant_raw = os.environ.get("TENANT_ID", "")
        device_raw = os.environ.get("DEVICE_ID", "")
        if not tenant_raw or not device_raw:
            raise ValueError("TENANT_ID and DEVICE_ID are required")
        return cls(
            tenant_id=uuid.UUID(tenant_raw),
            device_id=uuid.UUID(device_raw),
            mqtt_broker=os.environ.get("MQTT_BROKER", "emqx"),
            mqtt_port=int(os.environ.get("MQTT_BROKER_PORT", "1883")),
            mqtt_username=os.environ.get("MQTT_USERNAME", ""),
            mqtt_password=os.environ.get("MQTT_PASSWORD", ""),
            emit_interval_seconds=float(os.environ.get("EMIT_INTERVAL", "30")),
            http_port=int(os.environ.get("SIMULATOR_HTTP_PORT", "8090")),
        )


class MeshPublisher(Protocol):
    async def publish_mesh(
        self,
        domain: MeshDomain,
        event_type: str,
        payload: dict[str, JsonValue],
        context: dict[str, JsonValue] | None = None,
    ) -> uuid.UUID: ...


class InMemoryMeshPublisher:
    def __init__(self, env: SimulatorEnv) -> None:
        self.env = env
        self.events: list[dict[str, JsonValue]] = []

    async def publish_mesh(
        self,
        domain: MeshDomain,
        event_type: str,
        payload: dict[str, JsonValue],
        context: dict[str, JsonValue] | None = None,
    ) -> uuid.UUID:
        event_id = uuid.uuid4()
        envelope: dict[str, JsonValue] = {
            "event_id": str(event_id),
            "tenant_id": str(self.env.tenant_id),
            "device_id": str(self.env.device_id),
            "domain": domain.value,
            "event_type": event_type,
            "timestamp": datetime.now(tz=UTC).isoformat(),
            "payload": payload,
            "context": context or {},
            "correlation_id": None,
            "parent_event_id": None,
        }
        self.events.append(envelope)
        return event_id


def build_mesh_envelope(
    env: SimulatorEnv,
    domain: MeshDomain,
    event_type: str,
    payload: dict[str, JsonValue],
    context: dict[str, JsonValue] | None = None,
) -> tuple[uuid.UUID, str, dict[str, JsonValue]]:
    event_id = uuid.uuid4()
    envelope: dict[str, JsonValue] = {
        "event_id": str(event_id),
        "tenant_id": str(env.tenant_id),
        "device_id": str(env.device_id),
        "domain": domain.value,
        "event_type": event_type,
        "timestamp": datetime.now(tz=UTC).isoformat(),
        "payload": payload,
        "context": context or {},
        "correlation_id": None,
        "parent_event_id": None,
    }
    topic = mesh_event_topic(str(env.tenant_id), domain, event_type)
    return event_id, topic, envelope


class MqttMeshPublisher:
    def __init__(self, env: SimulatorEnv, client: aiomqtt.Client) -> None:
        self._env = env
        self._client = client

    async def publish_mesh(
        self,
        domain: MeshDomain,
        event_type: str,
        payload: dict[str, JsonValue],
        context: dict[str, JsonValue] | None = None,
    ) -> uuid.UUID:
        event_id, topic, envelope = build_mesh_envelope(self._env, domain, event_type, payload, context)
        body = json.dumps(envelope)
        await self._client.publish(topic, body)
        return event_id


def command_topic(tenant_id: uuid.UUID, device_id: uuid.UUID) -> str:
    return f"next-iot/{tenant_id}/devices/{device_id}/command"


def telemetry_topic(tenant_id: uuid.UUID, device_id: uuid.UUID) -> str:
    return f"tenants/{tenant_id}/devices/{device_id}/telemetry"
