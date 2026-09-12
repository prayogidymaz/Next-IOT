import uuid
from datetime import datetime

import redis.asyncio as aioredis
from fastapi import APIRouter, Depends, Query
from fastapi.responses import Response
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.dependencies import RequireAuth
from app.deps import get_db, get_redis
from app.devices.dependencies import CurrentDevice, get_current_device
from app.telemetry import service
from app.telemetry.anomaly_detector import get_anomalies
from app.telemetry.flight_replay import get_flight_replay
from app.telemetry.analytics import get_telemetry_analytics
from app.telemetry.export_service import export_telemetry
from app.telemetry.schemas import (
    FlightReplayResponse,
    SignalHeatmapResponse,
    SwarmMatrixResponse,
    TelemetryAnalyticsResponse,
    TelemetryAnomalyResponse,
    TelemetryIngestRequest,
    TelemetryIngestResponse,
    WeatherVectorResponse,
)
from app.telemetry.signal_heatmap import get_signal_heatmap
from app.telemetry.swarm_matrix import get_swarm_matrix
from app.telemetry.weather_vector import get_weather_vector

router = APIRouter(prefix="/api/v1/telemetry", tags=["telemetry"])


@router.post("", response_model=TelemetryIngestResponse, status_code=201)
async def ingest_telemetry(
    payload: TelemetryIngestRequest,
    device: CurrentDevice = Depends(get_current_device),
    db: AsyncSession = Depends(get_db),
    redis: aioredis.Redis = Depends(get_redis),
):
    """Ingest sensor telemetry from an authenticated online device."""
    return await service.ingest_telemetry(db, redis, device, payload)


@router.get("/signal-heatmap", response_model=SignalHeatmapResponse)
async def signal_heatmap(
    device_id: uuid.UUID,
    user: RequireAuth,
    db: AsyncSession = Depends(get_db),
    hours: int = Query(default=24, description="Lookback window in hours (1 or 24)"),
):
    """Return GPS + RSSI/SNR points for radio coverage heatmap visualization."""
    return await get_signal_heatmap(db, user, device_id=device_id, hours=hours)


@router.get("/anomalies", response_model=TelemetryAnomalyResponse)
async def telemetry_anomalies(
    device_id: uuid.UUID,
    user: RequireAuth,
    db: AsyncSession = Depends(get_db),
    hours: int = Query(default=24, description="Lookback window in hours (1 or 24)"),
):
    """Return detected telemetry anomaly history for a device."""
    return await get_anomalies(db, user, device_id=device_id, hours=hours)


@router.get("/flight-replay", response_model=FlightReplayResponse)
async def flight_replay(
    device_id: uuid.UUID,
    user: RequireAuth,
    db: AsyncSession = Depends(get_db),
    hours: int | None = Query(default=24, description="Lookback window in hours (1 or 24)"),
    start_time: datetime | None = Query(default=None, description="Flight session start (ISO-8601)"),
    end_time: datetime | None = Query(default=None, description="Flight session end (ISO-8601)"),
):
    """Return chronological telemetry samples for mission flight replay."""
    return await get_flight_replay(
        db,
        user,
        device_id=device_id,
        hours=hours,
        start_time=start_time,
        end_time=end_time,
    )


@router.get("/swarm-matrix", response_model=SwarmMatrixResponse)
async def swarm_matrix(
    user: RequireAuth,
    db: AsyncSession = Depends(get_db),
    redis: aioredis.Redis = Depends(get_redis),
):
    """Return pairwise drone distances and collision-risk warnings for the tenant swarm."""
    return await get_swarm_matrix(db, redis, user)


@router.get("/weather-vector", response_model=WeatherVectorResponse)
async def weather_vector(
    user: RequireAuth,
    lat: float = Query(..., ge=-90, le=90),
    lon: float = Query(..., ge=-180, le=180),
    radius: float = Query(default=2000.0, gt=0, le=20_000, alias="radius"),
):
    """Return mock/analyzed wind vector field and flight safety status for a mission area."""
    _ = user
    return await get_weather_vector(lat=lat, lon=lon, radius_m=radius)


@router.get("/export")
async def telemetry_export(
    device_id: uuid.UUID,
    user: RequireAuth,
    db: AsyncSession = Depends(get_db),
    export_format: str = Query(..., alias="format", description="Export format: csv, json, or kml"),
    hours: int = Query(default=24, description="Lookback window in hours (1 or 24)"),
):
    """Download full telemetry history in CSV, JSON, or KML format."""
    content, media_type, filename = await export_telemetry(
        db,
        user,
        device_id=device_id,
        export_format=export_format,
        hours=hours,
    )
    return Response(
        content=content,
        media_type=media_type,
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )


@router.get("/analytics", response_model=TelemetryAnalyticsResponse)
async def telemetry_analytics(
    device_id: uuid.UUID,
    user: RequireAuth,
    db: AsyncSession = Depends(get_db),
    hours: int = Query(default=24, description="Lookback window in hours (1 or 24)"),
):
    """Return flight statistics summary for a device telemetry window."""
    return await get_telemetry_analytics(db, user, device_id=device_id, hours=hours)
