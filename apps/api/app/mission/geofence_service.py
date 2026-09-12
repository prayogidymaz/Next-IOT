"""CRUD service for tenant geofence zones."""

from __future__ import annotations

import uuid
from datetime import UTC, datetime

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.dependencies import CurrentUser
from app.models.geofence_zone import GeofenceAction, GeofenceZone
from app.mission.geofence_checker import GeofenceZoneSnapshot
from app.mission.schemas import GeofenceCreateRequest, GeofenceUpdateRequest


def _validate_polygon(polygon_coords: list) -> None:
    if len(polygon_coords) < 3:
        raise ValueError("polygon_coords must contain at least 3 points")
    for point in polygon_coords:
        if not isinstance(point, dict):
            raise ValueError("Each polygon point must be an object with lat and lon")
        lat = point.get("lat")
        lon = point.get("lon")
        if lat is None or lon is None:
            raise ValueError("Each polygon point requires lat and lon")
        if not (-90 <= float(lat) <= 90):
            raise ValueError("lat must be between -90 and 90")
        if not (-180 <= float(lon) <= 180):
            raise ValueError("lon must be between -180 and 180")


def _validate_altitudes(min_altitude: float, max_altitude: float) -> None:
    if min_altitude < 0:
        raise ValueError("min_altitude must be >= 0")
    if max_altitude <= min_altitude:
        raise ValueError("max_altitude must be greater than min_altitude")


def _to_snapshot(zone: GeofenceZone) -> GeofenceZoneSnapshot:
    return GeofenceZoneSnapshot(
        id=str(zone.id),
        name=zone.name,
        polygon_coords=zone.polygon_coords,
        min_altitude=zone.min_altitude,
        max_altitude=zone.max_altitude,
        action_on_breach=zone.action_on_breach,
    )


def _serialize_zone(zone: GeofenceZone) -> dict:
    return {
        "id": zone.id,
        "tenant_id": zone.tenant_id,
        "name": zone.name,
        "polygon_coords": zone.polygon_coords,
        "max_altitude": zone.max_altitude,
        "min_altitude": zone.min_altitude,
        "action_on_breach": zone.action_on_breach,
        "created_at": zone.created_at,
        "updated_at": zone.updated_at,
    }


class GeofenceService:
    async def list_zones(self, db: AsyncSession, user: CurrentUser) -> list[dict]:
        query = select(GeofenceZone).where(GeofenceZone.tenant_id == user.tenant_id).order_by(GeofenceZone.name)
        rows = (await db.scalars(query)).all()
        return [_serialize_zone(row) for row in rows]

    async def get_zone(self, db: AsyncSession, user: CurrentUser, zone_id: uuid.UUID) -> dict:
        zone = await self._get_zone_for_user(db, user, zone_id)
        return _serialize_zone(zone)

    async def create_zone(self, db: AsyncSession, user: CurrentUser, payload: GeofenceCreateRequest) -> dict:
        _validate_polygon([p.model_dump() for p in payload.polygon_coords])
        _validate_altitudes(payload.min_altitude, payload.max_altitude)

        zone = GeofenceZone(
            tenant_id=user.tenant_id,
            name=payload.name.strip(),
            polygon_coords=[p.model_dump() for p in payload.polygon_coords],
            max_altitude=payload.max_altitude,
            min_altitude=payload.min_altitude,
            action_on_breach=payload.action_on_breach.value,
        )
        db.add(zone)
        await db.flush()
        await db.refresh(zone)
        return _serialize_zone(zone)

    async def update_zone(
        self,
        db: AsyncSession,
        user: CurrentUser,
        zone_id: uuid.UUID,
        payload: GeofenceUpdateRequest,
    ) -> dict:
        zone = await self._get_zone_for_user(db, user, zone_id)

        if payload.name is not None:
            zone.name = payload.name.strip()
        if payload.polygon_coords is not None:
            _validate_polygon([p.model_dump() for p in payload.polygon_coords])
            zone.polygon_coords = [p.model_dump() for p in payload.polygon_coords]
        if payload.min_altitude is not None:
            zone.min_altitude = payload.min_altitude
        if payload.max_altitude is not None:
            zone.max_altitude = payload.max_altitude
        if payload.action_on_breach is not None:
            zone.action_on_breach = payload.action_on_breach.value

        zone.updated_at = datetime.now(UTC)
        _validate_altitudes(zone.min_altitude, zone.max_altitude)
        await db.flush()
        await db.refresh(zone)
        return _serialize_zone(zone)

    async def delete_zone(self, db: AsyncSession, user: CurrentUser, zone_id: uuid.UUID) -> None:
        zone = await self._get_zone_for_user(db, user, zone_id)
        await db.delete(zone)
        await db.flush()

    async def fetch_snapshots_for_tenant(self, db: AsyncSession, tenant_id: uuid.UUID) -> list[GeofenceZoneSnapshot]:
        query = select(GeofenceZone).where(GeofenceZone.tenant_id == tenant_id)
        rows = (await db.scalars(query)).all()
        return [_to_snapshot(row) for row in rows]

    async def _get_zone_for_user(
        self,
        db: AsyncSession,
        user: CurrentUser,
        zone_id: uuid.UUID,
    ) -> GeofenceZone:
        query = select(GeofenceZone).where(
            GeofenceZone.id == zone_id,
            GeofenceZone.tenant_id == user.tenant_id,
        )
        zone = await db.scalar(query)
        if zone is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Geofence zone not found")
        return zone


geofence_service = GeofenceService()
