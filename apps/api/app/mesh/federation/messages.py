"""Federation message types (proto-compatible JSON transport)."""

from __future__ import annotations

import json
import uuid
from dataclasses import dataclass
from datetime import UTC, datetime

from app.mesh.federation import protocol_pb2
from app.types.json_types import JsonObject


@dataclass(slots=True)
class FederationMeshEvent:
    origin_site: str
    event_type: str
    device_id: str
    payload_json: str
    timestamp: int
    ttl: int

    @classmethod
    def from_local(
        cls,
        origin_site: str,
        event_type: str,
        device_id: uuid.UUID,
        payload: JsonObject,
        ttl: int = 8,
    ) -> FederationMeshEvent:
        return cls(
            origin_site=origin_site,
            event_type=event_type,
            device_id=str(device_id),
            payload_json=json.dumps(payload, ensure_ascii=False),
            timestamp=int(datetime.now(tz=UTC).timestamp()),
            ttl=ttl,
        )

    def payload(self) -> JsonObject:
        parsed = json.loads(self.payload_json)
        if isinstance(parsed, dict):
            return parsed
        return {}

    @classmethod
    def from_proto(cls, message: protocol_pb2.MeshEvent) -> FederationMeshEvent:
        return cls(
            origin_site=message.origin_site,
            event_type=message.event_type,
            device_id=message.device_id,
            payload_json=message.payload_json,
            timestamp=int(message.timestamp),
            ttl=int(message.ttl),
        )

    @staticmethod
    def to_proto(event: FederationMeshEvent) -> protocol_pb2.MeshEvent:
        return protocol_pb2.MeshEvent(
            origin_site=event.origin_site,
            event_type=event.event_type,
            device_id=event.device_id,
            payload_json=event.payload_json,
            timestamp=event.timestamp,
            ttl=event.ttl,
        )
