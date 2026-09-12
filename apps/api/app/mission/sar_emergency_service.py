"""SAR emergency response dispatcher — incident lifecycle, grid generation, alerts."""

from __future__ import annotations

import uuid
from datetime import UTC, datetime
from typing import Any

import redis.asyncio as aioredis
from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.dependencies import CurrentUser
from app.devices.service import _get_device_for_user
from app.mission.sar_emergency_events import publish_sar_emergency_alert
from app.mission.sar_grid_service import SarGridService
from app.mission.schemas import SarIncidentCreateRequest, SarIncidentUpdateRequest
from app.models.sar_incident import SarIncident, SarIncidentStatus, SarIncidentType

DEFAULT_SEARCH_RADIUS_M = 500.0
DEFAULT_LEG_SPACING_M = 100.0

_AUTO_CRASH_ANOMALIES = frozenset({"speed_deviation", "altitude_deviation"})


def _serialize_incident(incident: SarIncident) -> dict[str, Any]:
    return {
        "id": incident.id,
        "tenant_id": incident.tenant_id,
        "incident_type": incident.incident_type,
        "status": incident.status,
        "target_lat": incident.target_lat,
        "target_lon": incident.target_lon,
        "severity": incident.severity,
        "assigned_device_id": incident.assigned_device_id,
        "message": incident.message,
        "sar_grid": incident.sar_grid or {},
        "metadata": incident.metadata_ or {},
        "created_at": incident.created_at,
        "updated_at": incident.updated_at,
        "resolved_at": incident.resolved_at,
    }


class SarEmergencyResponseService:
    def __init__(self) -> None:
        self._grid_service = SarGridService()

    def _generate_sar_grid(self, lat: float, lon: float) -> dict[str, Any]:
        return self._grid_service.generate(
            lkp_lat=lat,
            lkp_lon=lon,
            radius_m=DEFAULT_SEARCH_RADIUS_M,
            pattern="expanding_square",
            leg_spacing_m=DEFAULT_LEG_SPACING_M,
        )

    async def list_incidents(
        self,
        db: AsyncSession,
        user: CurrentUser,
        *,
        status_filter: str | None = None,
    ) -> list[dict[str, Any]]:
        query = select(SarIncident).where(SarIncident.tenant_id == user.tenant_id)
        if status_filter:
            query = query.where(SarIncident.status == status_filter)
        query = query.order_by(SarIncident.created_at.desc())
        rows = (await db.scalars(query)).all()
        return [_serialize_incident(row) for row in rows]

    async def create_incident(
        self,
        db: AsyncSession,
        redis: aioredis.Redis,
        user: CurrentUser,
        payload: SarIncidentCreateRequest,
    ) -> dict[str, Any]:
        assigned_device_id = payload.assigned_device_id
        if assigned_device_id is not None:
            await _get_device_for_user(db, assigned_device_id, user)

        sar_grid = self._generate_sar_grid(payload.target_lat, payload.target_lon)
        incident = SarIncident(
            tenant_id=user.tenant_id,
            incident_type=payload.incident_type.value,
            status=SarIncidentStatus.ACTIVE.value,
            target_lat=payload.target_lat,
            target_lon=payload.target_lon,
            severity=payload.severity,
            assigned_device_id=assigned_device_id,
            message=payload.message,
            sar_grid=sar_grid,
            metadata_=payload.metadata or {},
        )
        db.add(incident)
        await db.flush()
        await db.refresh(incident)

        serialized = _serialize_incident(incident)
        await publish_sar_emergency_alert(
            redis,
            tenant_id=str(user.tenant_id),
            event_type="sar.incident.created",
            incident=serialized,
        )
        return serialized

    async def update_incident(
        self,
        db: AsyncSession,
        redis: aioredis.Redis,
        user: CurrentUser,
        incident_id: uuid.UUID,
        payload: SarIncidentUpdateRequest,
    ) -> dict[str, Any]:
        incident = await self._get_incident_for_user(db, user, incident_id)

        if payload.status is not None:
            incident.status = payload.status.value
            if payload.status == SarIncidentStatus.RESOLVED:
                incident.resolved_at = datetime.now(UTC)
        if payload.assigned_device_id is not None:
            await _get_device_for_user(db, payload.assigned_device_id, user)
            incident.assigned_device_id = payload.assigned_device_id
        if payload.severity is not None:
            incident.severity = payload.severity
        if payload.message is not None:
            incident.message = payload.message
        if payload.regenerate_grid:
            incident.sar_grid = self._generate_sar_grid(incident.target_lat, incident.target_lon)

        incident.updated_at = datetime.now(UTC)
        await db.flush()
        await db.refresh(incident)

        serialized = _serialize_incident(incident)
        event_type = (
            "sar.incident.resolved"
            if incident.status == SarIncidentStatus.RESOLVED.value
            else "sar.incident.updated"
        )
        await publish_sar_emergency_alert(
            redis,
            tenant_id=str(user.tenant_id),
            event_type=event_type,
            incident=serialized,
        )
        return serialized

    async def trigger_from_anomaly(
        self,
        db: AsyncSession,
        redis: aioredis.Redis,
        *,
        tenant_id: uuid.UUID,
        device_id: uuid.UUID,
        anomaly_type: str,
        severity: str,
        message: str,
        metadata: dict[str, Any],
    ) -> dict[str, Any] | None:
        if severity != "critical" or anomaly_type not in _AUTO_CRASH_ANOMALIES:
            return None

        lat = metadata.get("lat")
        lon = metadata.get("lon")
        if lat is None or lon is None:
            return None

        existing = await db.scalar(
            select(SarIncident).where(
                SarIncident.tenant_id == tenant_id,
                SarIncident.status == SarIncidentStatus.ACTIVE.value,
                SarIncident.incident_type == SarIncidentType.DRONE_DOWN.value,
                SarIncident.assigned_device_id == device_id,
            )
        )
        if existing is not None:
            return None

        sar_grid = self._generate_sar_grid(float(lat), float(lon))
        incident = SarIncident(
            tenant_id=tenant_id,
            incident_type=SarIncidentType.DRONE_DOWN.value,
            status=SarIncidentStatus.ACTIVE.value,
            target_lat=float(lat),
            target_lon=float(lon),
            severity="critical",
            assigned_device_id=device_id,
            message=message,
            sar_grid=sar_grid,
            metadata_={"auto_triggered": True, "anomaly_type": anomaly_type, **metadata},
        )
        db.add(incident)
        await db.flush()
        await db.refresh(incident)

        serialized = _serialize_incident(incident)
        await publish_sar_emergency_alert(
            redis,
            tenant_id=str(tenant_id),
            event_type="sar.incident.auto_created",
            incident=serialized,
        )
        return serialized

    async def trigger_from_ai_detection(
        self,
        db: AsyncSession,
        redis: aioredis.Redis,
        *,
        tenant_id: uuid.UUID,
        device_id: uuid.UUID,
        detection_class: str,
        lat: float,
        lon: float,
        confidence: float,
    ) -> dict[str, Any]:
        detection = detection_class.lower()
        if detection in {"person", "human", "pedestrian"}:
            incident_type = SarIncidentType.PERSON_LOST
        elif detection in {"vehicle", "car", "truck"}:
            incident_type = SarIncidentType.VEHICLE_CRASH
        else:
            incident_type = SarIncidentType.PERSON_LOST

        sar_grid = self._generate_sar_grid(lat, lon)
        incident = SarIncident(
            tenant_id=tenant_id,
            incident_type=incident_type.value,
            status=SarIncidentStatus.ACTIVE.value,
            target_lat=lat,
            target_lon=lon,
            severity="critical",
            assigned_device_id=device_id,
            message=f"AI detected {detection_class} (confidence {confidence:.0%})",
            sar_grid=sar_grid,
            metadata_={
                "auto_triggered": True,
                "source": "ai_detection",
                "detection_class": detection_class,
                "confidence": confidence,
            },
        )
        db.add(incident)
        await db.flush()
        await db.refresh(incident)

        serialized = _serialize_incident(incident)
        await publish_sar_emergency_alert(
            redis,
            tenant_id=str(tenant_id),
            event_type="sar.incident.ai_created",
            incident=serialized,
        )
        return serialized

    async def _get_incident_for_user(
        self,
        db: AsyncSession,
        user: CurrentUser,
        incident_id: uuid.UUID,
    ) -> SarIncident:
        query = select(SarIncident).where(
            SarIncident.id == incident_id,
            SarIncident.tenant_id == user.tenant_id,
        )
        incident = await db.scalar(query)
        if incident is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="SAR incident not found")
        return incident


sar_emergency_service = SarEmergencyResponseService()
