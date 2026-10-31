"""Kubernetes-style health probes."""

from __future__ import annotations

import logging

import redis.asyncio as aioredis
from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse
from sqlalchemy import text

from app.config import settings
from app.database import engine
from app.system.health import collect_system_health
logger = logging.getLogger(__name__)

router = APIRouter(tags=["health"])


@router.get("/health/live")
async def health_live() -> JSONResponse:
    return JSONResponse(status_code=200, content={"status": "alive", "service": settings.app_name})


@router.get("/health/startup")
async def health_startup(request: Request) -> JSONResponse:
    ready = bool(getattr(request.app.state, "startup_ready", False))
    code = 200 if ready else 503
    return JSONResponse(
        status_code=code,
        content={
            "status": "ready" if ready else "starting",
            "service": settings.app_name,
            "bootstrap": "ok" if ready else "pending",
        },
    )


async def _alembic_ok() -> str:
    try:
        async with engine.connect() as conn:
            result = await conn.execute(text("SELECT version_num FROM alembic_version LIMIT 1"))
            row = result.first()
            if row is None:
                return "missing"
            return "ok"
    except Exception:
        logger.debug("Alembic version check failed", exc_info=True)
        return "fail"


@router.get("/health/ready")
async def health_ready(request: Request) -> JSONResponse:
    if not bool(getattr(request.app.state, "startup_ready", False)):
        return JSONResponse(
            status_code=503,
            content={"status": "not_ready", "reason": "startup_pending"},
        )

    redis_raw: object = getattr(request.app.state, "redis", None)
    redis_client: aioredis.Redis | None
    if isinstance(redis_raw, aioredis.Redis):
        redis_client = redis_raw
    else:
        redis_client = None

    system = await collect_system_health(engine=engine, redis=redis_client)
    migrations = await _alembic_ok()
    components = dict(system.get("components", {}))
    components["migrations"] = migrations
    components["emqx"] = components.get("mqtt_broker", "unknown")

    critical_ok = (
        components.get("database") == "ok"
        and components.get("redis_cache") == "ok"
        and migrations == "ok"
    )
    status = "ready" if critical_ok and system.get("status") == "ready" else "degraded"
    code = 200 if status == "ready" else 503

    return JSONResponse(
        status_code=code,
        content={
            "status": status,
            "service": settings.app_name,
            "environment": settings.app_env,
            "components": components,
            "system_metrics": system.get("system_metrics"),
        },
    )
