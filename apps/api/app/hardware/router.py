import redis.asyncio as aioredis
from fastapi import APIRouter, Depends

from app.auth.dependencies import RequireAuth
from app.deps import get_redis
from app.hardware import cyberdeck_ptt
from app.hardware.cyberdeck_schemas import (
    CyberdeckHealthResponse,
    CyberdeckMeshResponse,
    PttBeaconRequest,
    PttDispatchResponse,
    PttTextDispatchRequest,
)
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


@router.get("/cyberdeck/mesh", response_model=CyberdeckMeshResponse)
async def get_cyberdeck_mesh(_: RequireAuth, redis: aioredis.Redis = Depends(get_redis)):
    return await cyberdeck_ptt.get_mesh_nodes(redis)


@router.get("/cyberdeck/health", response_model=CyberdeckHealthResponse)
async def get_cyberdeck_health(_: RequireAuth, redis: aioredis.Redis = Depends(get_redis)):
    return await cyberdeck_ptt.get_cyberdeck_health(redis)


@router.post("/cyberdeck/ptt/text", response_model=PttDispatchResponse, status_code=201)
async def cyberdeck_ptt_text(
    payload: PttTextDispatchRequest,
    _: RequireAuth,
    redis: aioredis.Redis = Depends(get_redis),
):
    return await cyberdeck_ptt.dispatch_text(redis, payload)


@router.post("/cyberdeck/ptt/beacon", response_model=PttDispatchResponse, status_code=201)
async def cyberdeck_ptt_beacon(
    payload: PttBeaconRequest,
    _: RequireAuth,
    redis: aioredis.Redis = Depends(get_redis),
):
    return await cyberdeck_ptt.dispatch_beacon(redis, payload)
