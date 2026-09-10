from typing import Annotated

import redis.asyncio as aioredis
from fastapi import APIRouter, Depends, Query

from app.auth.dependencies import CurrentUser, require_roles
from app.auth.rbac import UserRole
from app.deps import get_redis

RequireDeviceReader = Annotated[
    CurrentUser,
    Depends(require_roles(UserRole.VIEWER, UserRole.OPERATOR, UserRole.TENANT_ADMIN, UserRole.SUPER_ADMIN)),
]
from app.rules.alert_schemas import AlertListResponse, AlertResponse, AlertSummaryResponse
from app.rules.alerts import list_alerts

router = APIRouter(prefix="/api/v1/alerts", tags=["alerts"])


@router.get("", response_model=AlertListResponse)
async def get_alerts(
    user: RequireDeviceReader,
    redis: aioredis.Redis = Depends(get_redis),
    status: str | None = Query(default=None, description="Filter: active, history, or omit for all"),
    limit: int = Query(default=50, ge=1, le=200),
):
    items = await list_alerts(
        redis,
        tenant_id=str(user.tenant_id),
        is_super_admin=user.is_super_admin,
        status=status,
        limit=limit,
    )
    return AlertListResponse(
        count=len(items),
        items=[AlertResponse.model_validate(item) for item in items],
    )


@router.get("/summary", response_model=AlertSummaryResponse)
async def get_alerts_summary(
    user: RequireDeviceReader,
    redis: aioredis.Redis = Depends(get_redis),
    limit: int = Query(default=5, ge=1, le=20),
):
    active = await list_alerts(
        redis,
        tenant_id=str(user.tenant_id),
        is_super_admin=user.is_super_admin,
        status="active",
        limit=limit,
    )
    return AlertSummaryResponse(
        active_count=len(active),
        items=[AlertResponse.model_validate(item) for item in active],
    )
