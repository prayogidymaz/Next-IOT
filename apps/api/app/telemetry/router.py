import redis.asyncio as aioredis
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.deps import get_db, get_redis
from app.devices.dependencies import CurrentDevice, get_current_device
from app.telemetry import service
from app.telemetry.schemas import TelemetryIngestRequest, TelemetryIngestResponse

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
