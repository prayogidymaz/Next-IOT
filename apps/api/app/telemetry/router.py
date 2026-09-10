import uuid

import redis.asyncio as aioredis
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.dependencies import RequireAuth
from app.deps import get_db, get_redis
from app.devices.dependencies import CurrentDevice, get_current_device
from app.telemetry import service
from app.telemetry.anomaly_detector import get_anomalies
from app.telemetry.schemas import (
    SignalHeatmapResponse,
    TelemetryAnomalyResponse,
    TelemetryIngestRequest,
    TelemetryIngestResponse,
)
from app.telemetry.signal_heatmap import get_signal_heatmap

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
