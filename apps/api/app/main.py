import asyncio
import logging
from contextlib import asynccontextmanager

import redis.asyncio as aioredis
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy import text

from app.api.v1.router import router as v1_router
from app.auth.router import router as auth_router
from app.config import settings
from app.database import engine
from app.devices.router import router as devices_router
from app.rules.alert_router import router as alerts_router
from app.rules.router import router as rules_router
from app.database import async_session
from app.models.user import User
from app.seed import ensure_default_admin, run_seed
from app.seed_telemetry import run_telemetry_seed
from sqlalchemy import select
from app.telemetry.router import router as telemetry_router
from app.devices.worker import offline_checker_loop
from app.notifications.router import router as notifications_router
from app.notifications.worker import notification_dispatcher_loop
from app.hardware.router import router as hardware_router
from app.tiles.router import router as tiles_router
from app.seed_hardware import run_hardware_seed

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    redis = aioredis.from_url(settings.redis_url, decode_responses=True)
    app.state.redis = redis

    if settings.seed_default_admin:
        try:
            await run_seed()
        except Exception:
            logger.exception("Default admin seed failed")

    if settings.seed_demo_telemetry:
        try:
            await run_telemetry_seed(redis)
        except Exception:
            logger.exception("Demo telemetry seed failed")

    if settings.seed_demo_telemetry:
        try:
            await run_hardware_seed(redis)
        except Exception:
            logger.exception("Demo hardware seed failed")

    stop_event = asyncio.Event()
    offline_worker_task = asyncio.create_task(offline_checker_loop(redis, stop_event))
    notification_worker_task = asyncio.create_task(notification_dispatcher_loop(redis, stop_event))
    app.state.offline_worker_stop = stop_event

    yield

    stop_event.set()
    for task in (offline_worker_task, notification_worker_task):
        task.cancel()
        try:
            await task
        except asyncio.CancelledError:
            pass
    await redis.aclose()
    await engine.dispose()


app = FastAPI(
    title=settings.app_name,
    version="0.10.0",
    description="Next-IOT Platform API",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=settings.cors_allow_credentials,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router)
app.include_router(v1_router)
app.include_router(devices_router)
app.include_router(telemetry_router)
app.include_router(rules_router)
app.include_router(alerts_router)
app.include_router(notifications_router)
app.include_router(hardware_router)
app.include_router(tiles_router)


@app.get("/health")
async def health_check():
    db_ok = False
    redis_ok = False

    try:
        async with engine.connect() as conn:
            await conn.execute(text("SELECT 1"))
            db_ok = True
    except Exception:
        pass

    if db_ok and settings.app_env == "development" and settings.seed_default_admin:
        try:
            async with async_session() as db:
                admin = await db.scalar(select(User).where(User.email == settings.seed_admin_email))
                if admin is None:
                    await ensure_default_admin(db)
                    logger.info("Re-seeded missing default admin on health check")
        except Exception:
            logger.exception("Dev admin self-heal failed")

    try:
        redis = app.state.redis
        if redis:
            await redis.ping()
            redis_ok = True
    except Exception:
        pass

    status = "healthy" if db_ok and redis_ok else "degraded"
    code = 200 if status == "healthy" else 503

    return JSONResponse(
        status_code=code,
        content={
            "status": status,
            "service": settings.app_name,
            "environment": settings.app_env,
            "checks": {
                "database": "ok" if db_ok else "fail",
                "redis": "ok" if redis_ok else "fail",
            },
        },
    )
