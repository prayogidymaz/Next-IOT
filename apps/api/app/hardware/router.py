import redis.asyncio as aioredis
from fastapi import APIRouter, Depends, Request

from app.auth.dependencies import RequireAuth
from app.deps import get_redis
from app.hardware.lora_bridge import read_gateway_status
from app.hardware.schemas import GatewayStatusResponse

router = APIRouter(prefix="/api/v1/hardware", tags=["hardware"])


@router.get("/gateway-status", response_model=GatewayStatusResponse)
async def get_hardware_gateway_status(
    _: RequireAuth,
    redis: aioredis.Redis = Depends(get_redis),
):
    status = await read_gateway_status(redis)
    return GatewayStatusResponse.model_validate(status)
