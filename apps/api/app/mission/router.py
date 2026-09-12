import uuid

import redis.asyncio as aioredis
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.dependencies import RequireOperator
from app.deps import get_db, get_redis
from app.mission import sar_grid_service
from app.mission.geofence_service import geofence_service
from app.mission.sar_emergency_service import sar_emergency_service
from app.mission.schemas import (
    GeofenceCreateRequest,
    GeofenceListResponse,
    GeofenceUpdateRequest,
    GeofenceZoneResponse,
    SarGridRequest,
    SarGridResponse,
    SarIncidentCreateRequest,
    SarIncidentListResponse,
    SarIncidentResponse,
    SarIncidentUpdateRequest,
)

router = APIRouter(prefix="/api/v1/mission", tags=["mission"])

_sar_service = sar_grid_service.SarGridService()


@router.post("/sar-grid", response_model=SarGridResponse)
async def generate_sar_grid(payload: SarGridRequest, _user: RequireOperator):
    try:
        result = _sar_service.generate(
            lkp_lat=payload.lkp_lat,
            lkp_lon=payload.lkp_lon,
            radius_m=payload.radius_m,
            pattern=payload.pattern.value,
            leg_spacing_m=payload.leg_spacing_m,
        )
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(exc)) from exc

    return SarGridResponse.model_validate(result)


@router.get("/geofence", response_model=GeofenceListResponse)
async def list_geofence_zones(
    user: RequireOperator,
    db: AsyncSession = Depends(get_db),
):
    items = await geofence_service.list_zones(db, user)
    return GeofenceListResponse(
        count=len(items),
        items=[GeofenceZoneResponse.model_validate(item) for item in items],
    )


@router.get("/geofence/{zone_id}", response_model=GeofenceZoneResponse)
async def get_geofence_zone(
    zone_id: uuid.UUID,
    user: RequireOperator,
    db: AsyncSession = Depends(get_db),
):
    item = await geofence_service.get_zone(db, user, zone_id)
    return GeofenceZoneResponse.model_validate(item)


@router.post("/geofence", response_model=GeofenceZoneResponse, status_code=status.HTTP_201_CREATED)
async def create_geofence_zone(
    payload: GeofenceCreateRequest,
    user: RequireOperator,
    db: AsyncSession = Depends(get_db),
):
    try:
        item = await geofence_service.create_zone(db, user, payload)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(exc)) from exc
    return GeofenceZoneResponse.model_validate(item)


@router.put("/geofence/{zone_id}", response_model=GeofenceZoneResponse)
async def update_geofence_zone(
    zone_id: uuid.UUID,
    payload: GeofenceUpdateRequest,
    user: RequireOperator,
    db: AsyncSession = Depends(get_db),
):
    try:
        item = await geofence_service.update_zone(db, user, zone_id, payload)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(exc)) from exc
    return GeofenceZoneResponse.model_validate(item)


@router.delete("/geofence/{zone_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_geofence_zone(
    zone_id: uuid.UUID,
    user: RequireOperator,
    db: AsyncSession = Depends(get_db),
):
    await geofence_service.delete_zone(db, user, zone_id)


@router.get("/sar-incidents", response_model=SarIncidentListResponse)
async def list_sar_incidents(
    user: RequireOperator,
    db: AsyncSession = Depends(get_db),
    status_filter: str | None = Query(default=None, alias="status"),
):
    items = await sar_emergency_service.list_incidents(db, user, status_filter=status_filter)
    return SarIncidentListResponse(
        count=len(items),
        items=[SarIncidentResponse.model_validate(item) for item in items],
    )


@router.post("/sar-incidents", response_model=SarIncidentResponse, status_code=status.HTTP_201_CREATED)
async def create_sar_incident(
    payload: SarIncidentCreateRequest,
    user: RequireOperator,
    db: AsyncSession = Depends(get_db),
    redis: aioredis.Redis = Depends(get_redis),
):
    item = await sar_emergency_service.create_incident(db, redis, user, payload)
    return SarIncidentResponse.model_validate(item)


@router.patch("/sar-incidents/{incident_id}", response_model=SarIncidentResponse)
async def update_sar_incident(
    incident_id: uuid.UUID,
    payload: SarIncidentUpdateRequest,
    user: RequireOperator,
    db: AsyncSession = Depends(get_db),
    redis: aioredis.Redis = Depends(get_redis),
):
    item = await sar_emergency_service.update_incident(db, redis, user, incident_id, payload)
    return SarIncidentResponse.model_validate(item)
