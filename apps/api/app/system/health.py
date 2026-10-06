from __future__ import annotations

import asyncio
import socket

import redis.asyncio as aioredis
from app.config import settings
from pydantic import JsonValue
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncEngine


def _system_metrics() -> dict[str, JsonValue]:
    try:
        import psutil

        return {
            "cpu_percent": psutil.cpu_percent(interval=0.1),
            "memory_percent": psutil.virtual_memory().percent,
            "memory_available_mb": round(psutil.virtual_memory().available / (1024 * 1024), 1),
        }
    except Exception:
        return {"cpu_percent": None, "memory_percent": None, "memory_available_mb": None}


async def _check_postgres(engine: AsyncEngine) -> str:
    try:
        async with engine.connect() as conn:
            await conn.execute(text("SELECT 1"))
        return "ok"
    except Exception:
        return "fail"


async def _check_redis(redis: aioredis.Redis | None) -> str:
    if redis is None:
        return "fail"
    try:
        await redis.ping()
        return "ok"
    except Exception:
        return "fail"


def _check_mqtt_broker() -> str:
    """TCP probe optional MQTT broker; Redis pub/sub is the primary command bus when unset."""
    host = settings.mqtt_broker_host.strip()
    port = settings.mqtt_broker_port
    if not host:
        return "standby"
    try:
        with socket.create_connection((host, port), timeout=settings.mqtt_broker_timeout_seconds):
            return "ok"
    except OSError:
        if settings.app_env == "development":
            return "standby"
        return "fail"


async def collect_system_health(
    *,
    engine: AsyncEngine,
    redis: aioredis.Redis | None,
) -> dict[str, JsonValue]:
    db_status, redis_status = await asyncio.gather(
        _check_postgres(engine),
        _check_redis(redis),
    )
    mqtt_status = await asyncio.to_thread(_check_mqtt_broker)
    metrics = await asyncio.to_thread(_system_metrics)

    components = {
        "database": db_status,
        "redis_cache": redis_status,
        "mqtt_broker": mqtt_status,
    }
    critical_ok = db_status == "ok" and redis_status == "ok"
    mqtt_ok = mqtt_status in {"ok", "standby"}
    ready = critical_ok and mqtt_ok

    return {
        "status": "ready" if ready else "degraded",
        "service": settings.app_name,
        "environment": settings.app_env,
        "components": components,
        "system_metrics": metrics,
    }
