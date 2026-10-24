"""Pydantic schemas for Universal Mesh events."""

from __future__ import annotations

import uuid
from datetime import datetime
from typing import Self, cast

from pydantic import BaseModel, Field

from app.mesh.event_bus import MeshDomain
from app.types.json_types import JsonObject


class GeoLocation(BaseModel):
    lat: float
    lng: float


class MeshContext(BaseModel):
    farm_id: uuid.UUID | None = None
    plot_id: uuid.UUID | None = None
    geo_location: GeoLocation | None = None
    physical_zone: str | None = None
    capabilities: list[str] = Field(default_factory=list)


class MeshEvent(BaseModel):
    event_id: uuid.UUID
    tenant_id: uuid.UUID
    device_id: uuid.UUID
    domain: MeshDomain
    event_type: str
    timestamp: datetime
    payload: JsonObject
    context: MeshContext
    correlation_id: uuid.UUID | None = None
    parent_event_id: uuid.UUID | None = None


class MeshEventPublishRequest(BaseModel):
    device_id: uuid.UUID
    domain: MeshDomain
    event_type: str
    payload: JsonObject = Field(default_factory=dict)
    context: MeshContext | None = None
    correlation_id: uuid.UUID | None = None
    parent_event_id: uuid.UUID | None = None


class MeshEventResponse(BaseModel):
    event_id: uuid.UUID
    tenant_id: uuid.UUID
    device_id: uuid.UUID
    domain: MeshDomain
    event_type: str
    timestamp: datetime
    payload: JsonObject
    context: MeshContext
    correlation_id: uuid.UUID | None
    parent_event_id: uuid.UUID | None
    created_at: datetime

    @classmethod
    def from_record(cls, row: object) -> Self:
        from app.models.mesh_event import MeshEventRecord

        if not isinstance(row, MeshEventRecord):
            raise TypeError("expected MeshEventRecord")
        ctx_raw = row.context if isinstance(row.context, dict) else {}
        geo_raw = ctx_raw.get("geo_location")
        geo: GeoLocation | None = None
        if isinstance(geo_raw, dict):
            lat = geo_raw.get("lat")
            lng = geo_raw.get("lng")
            if isinstance(lat, int | float) and isinstance(lng, int | float):
                geo = GeoLocation(lat=float(lat), lng=float(lng))
        caps_raw = ctx_raw.get("capabilities")
        capabilities: list[str] = []
        if isinstance(caps_raw, list):
            capabilities = [c for c in caps_raw if isinstance(c, str)]
        farm_id = ctx_raw.get("farm_id")
        plot_id = ctx_raw.get("plot_id")
        zone_raw = ctx_raw.get("physical_zone")
        physical_zone = zone_raw if isinstance(zone_raw, str) else None
        context = MeshContext(
            farm_id=uuid.UUID(str(farm_id)) if isinstance(farm_id, str) else None,
            plot_id=uuid.UUID(str(plot_id)) if isinstance(plot_id, str) else None,
            geo_location=geo,
            physical_zone=physical_zone,
            capabilities=capabilities,
        )
        return cls(
            event_id=row.id,
            tenant_id=row.tenant_id,
            device_id=row.device_id,
            domain=MeshDomain(row.domain),
            event_type=row.event_type,
            timestamp=row.timestamp,
            # mesh_events.payload is JSONB written only by MeshEventPublisher (JsonObject).
            payload=cast(JsonObject, row.payload) if isinstance(row.payload, dict) else {},
            context=context,
            correlation_id=row.correlation_id,
            parent_event_id=row.parent_event_id,
            created_at=row.created_at,
        )
