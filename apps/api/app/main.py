import asyncio
import logging
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from typing import TypedDict, cast

import redis.asyncio as aioredis
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, Response
from prometheus_client import CONTENT_TYPE_LATEST, generate_latest
from sqlalchemy import select, text

from app.agriculture.router import router as agriculture_router
from app.agriculture.worker import agriculture_jobs_loop
from app.alarms.maintenance import alarm_maintenance_loop
from app.alarms.router import router as alarms_router
from app.analytics.ml.scheduler import ml_anomaly_scheduler_loop
from app.analytics.report_scheduler import analytics_report_scheduler_loop
from app.analytics.router import router as analytics_router
from app.api.v1.router import router as v1_router
from app.audit.middleware import AuditLoggingMiddleware
from app.audit.router import router as audit_router
from app.auth.router import router as auth_router
from app.automation.pipeline_listener import pipeline_listener_loop
from app.automation.router import router as automation_router
from app.billing.router import router as billing_router
from app.cameras.router import router as cameras_router
from app.config import settings
from app.database import async_session, engine
from app.device_claim_tokens.router import router as device_claim_tokens_router
from app.device_profiles.router import router as device_profiles_router
from app.devices.edge_agent.router import devices_router as edge_devices_router
from app.devices.edge_agent.router import firmware_router as edge_firmware_router
from app.devices.router import router as devices_router
from app.devices.worker import offline_checker_loop
from app.firmware_studio.router import router as firmware_studio_router
from app.hardware.router import router as hardware_router
from app.mavlink.router import router as mavlink_router
from app.mesh.ai_copilot.router import router as mesh_copilot_router
from app.mesh.federation.router import router as mesh_federation_router
from app.mesh.publisher import init_mesh_publisher
from app.mesh.router import router as mesh_router
from app.mesh.scheduler import mesh_schedule_loop
from app.mesh.workflow_executor import init_mesh_workflow_executor
from app.mesh.workflow_listener import mesh_workflow_listener_loop
from app.mesh.workflow_router import router as mesh_workflow_router
from app.workflows.analytics.router import router as workflow_analytics_router
from app.workflows.approval.router import approval_router, workflow_router as workflow_approval_workflow_router
from app.workflows.marketplace.router import router as workflow_marketplace_router
from app.workflows.versioning.router import router as workflow_versioning_router
from app.mission.router import router as mission_router
from app.mission.sar_emergency_router import router as sar_emergency_ws_router
from app.models.user import User
from app.mqtt_auth.emqx_rule_setup import setup_telemetry_forwarding_rule
from app.mqtt_auth.router import router as mqtt_auth_router
from app.mqtt_publisher import MqttPublisherService
from app.mqtt_publisher.noop import NoopMqttPublisher
from app.mqtt_subscriber import MqttSubscriberService
from app.notifications.fcm_router import router as fcm_router
from app.notifications.gateway_router import channels_router, log_router
from app.notifications.gateway_router import rules_router as notification_rules_router
from app.notifications.router import router as notifications_router
from app.notifications.worker import notification_dispatcher_loop
from app.ota.router import router as ota_router
from app.realtime.router import router as realtime_router
from app.rules.alert_router import router as alerts_router
from app.rules.executor import init_rule_executor
from app.rules.router import router as rules_router
from app.rules.scheduler import rule_schedule_loop
from app.seed import ensure_default_admin, run_seed
from app.seed_device_profiles import run_device_profile_seed
from app.seed_hardware import run_hardware_seed
from app.seed_telemetry import run_telemetry_seed
from app.super_admin.router import router as super_admin_router
from app.support.router import router as support_router
from app.system.router import router as system_router
from app.telemetry.retention import telemetry_retention_loop
from app.telemetry.router import router as telemetry_router
from app.telemetry.video_feed.router import router as video_feed_router
from app.telemetry.ws_router import router as telemetry_ws_router
from app.tenants.router import router as tenants_router
from app.tiles.router import router as tiles_router
from app.types.redis_client import (
    RedisClient,
    as_legacy_redis_stub,
    close_redis,
    redis_from_url,
)
from app.users.router import router as users_router
from app.vision.router import router as vision_router

logger = logging.getLogger(__name__)


class CorsMiddlewareKwargs(TypedDict, total=False):
    allow_credentials: bool
    allow_methods: list[str]
    allow_headers: list[str]
    expose_headers: list[str]
    allow_origin_regex: str
    allow_origins: list[str]


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    app.state.startup_ready = False
    redis: RedisClient = redis_from_url(settings.redis_url)
    app.state.redis = redis

    if settings.seed_default_admin:
        try:
            await run_seed()
        except Exception:
            logger.exception("Default admin seed failed")

    if settings.seed_demo_telemetry:
        try:
            await run_telemetry_seed(as_legacy_redis_stub(redis))
        except Exception:
            logger.exception("Demo telemetry seed failed")

    if settings.seed_demo_telemetry:
        try:
            await run_hardware_seed(as_legacy_redis_stub(redis))
        except Exception:
            logger.exception("Demo hardware seed failed")

    if settings.seed_demo_telemetry:
        try:
            await run_device_profile_seed()
        except Exception:
            logger.exception("Demo device profile seed failed")

    if settings.emqx_telemetry_rule_setup_enabled:
        try:
            await setup_telemetry_forwarding_rule()
        except Exception:
            logger.exception("EMQX telemetry rule setup failed")

    stop_event = asyncio.Event()
    worker_tasks: list[asyncio.Task[None]] = []
    mqtt_subscriber: MqttSubscriberService | None = None
    if settings.run_background_workers:
        worker_tasks = [
            asyncio.create_task(offline_checker_loop(redis, stop_event)),
            asyncio.create_task(notification_dispatcher_loop(redis, stop_event)),
            asyncio.create_task(pipeline_listener_loop(redis, stop_event)),
            asyncio.create_task(telemetry_retention_loop(stop_event)),
            asyncio.create_task(alarm_maintenance_loop(stop_event)),
            asyncio.create_task(rule_schedule_loop(stop_event)),
            asyncio.create_task(agriculture_jobs_loop(redis, stop_event)),
            asyncio.create_task(mesh_workflow_listener_loop(redis, stop_event)),
            asyncio.create_task(mesh_schedule_loop(redis, stop_event)),
            asyncio.create_task(analytics_report_scheduler_loop(stop_event)),
            asyncio.create_task(ml_anomaly_scheduler_loop(stop_event)),
        ]
    mqtt_publisher: MqttPublisherService | NoopMqttPublisher
    if settings.mqtt_publisher_enabled and settings.run_background_workers:
        mqtt_publisher = MqttPublisherService()
        worker_tasks.append(asyncio.create_task(mqtt_publisher.run()))
    else:
        mqtt_publisher = NoopMqttPublisher()
    app.state.mqtt_publisher = mqtt_publisher
    mesh_event_publisher = init_mesh_publisher(redis, mqtt_publisher)
    init_mesh_workflow_executor(redis, mesh_event_publisher, mqtt_publisher)
    rule_executor = init_rule_executor(redis, mqtt_publisher)
    await rule_executor.startup()
    app.state.rule_executor = rule_executor
    app.state.offline_worker_stop = stop_event
    app.state.startup_ready = True
    logger.info(
        "API fully ready (database, redis, mqtt_subscriber=%s, emqx_rule_setup=%s, workers)",
        settings.mqtt_subscriber_enabled,
        settings.emqx_telemetry_rule_setup_enabled,
    )
    if settings.mqtt_subscriber_enabled and settings.run_background_workers:
        mqtt_subscriber = MqttSubscriberService(redis, rule_executor=rule_executor)
        worker_tasks.append(asyncio.create_task(mqtt_subscriber.run()))
    app.state.mqtt_subscriber = mqtt_subscriber
    yield

    stop_event.set()
    if mqtt_subscriber is not None:
        mqtt_subscriber.request_stop()
    if isinstance(mqtt_publisher, MqttPublisherService):
        mqtt_publisher.request_stop()
    for task in worker_tasks:
        task.cancel()
        try:
            await task
        except asyncio.CancelledError:
            pass
    await close_redis(redis)
    await engine.dispose()


app = FastAPI(
    title=settings.app_name,
    version="0.10.0",
    description="Next-IOT Platform API",
    lifespan=lifespan,
)

_cors_kwargs: CorsMiddlewareKwargs = {
    "allow_credentials": settings.cors_allow_credentials,
    "allow_methods": ["*"],
    "allow_headers": ["*"],
    "expose_headers": ["Content-Disposition"],
}
if settings.cors_allow_origin_regex:
    _cors_kwargs["allow_origin_regex"] = settings.cors_allow_origin_regex
_cors_kwargs["allow_origins"] = settings.cors_origins_list
app.add_middleware(CORSMiddleware, **_cors_kwargs)
app.add_middleware(AuditLoggingMiddleware)

app.include_router(auth_router)
app.include_router(auth_router, prefix="/api/v1")
app.include_router(v1_router)
app.include_router(edge_devices_router)
app.include_router(edge_firmware_router)
app.include_router(devices_router)
app.include_router(device_profiles_router)
app.include_router(telemetry_router)
app.include_router(rules_router)
app.include_router(alerts_router)
app.include_router(alarms_router)
app.include_router(notifications_router)
app.include_router(fcm_router)
app.include_router(channels_router)
app.include_router(notification_rules_router)
app.include_router(log_router)
app.include_router(hardware_router)
app.include_router(tiles_router)
app.include_router(mission_router)
app.include_router(device_claim_tokens_router)
app.include_router(mqtt_auth_router)
app.include_router(sar_emergency_ws_router)
app.include_router(video_feed_router)
app.include_router(telemetry_ws_router)
app.include_router(realtime_router)
app.include_router(mavlink_router)
app.include_router(automation_router)
app.include_router(ota_router)
app.include_router(firmware_studio_router)
app.include_router(billing_router)
app.include_router(super_admin_router)
app.include_router(support_router)
app.include_router(agriculture_router)
app.include_router(mesh_router)
app.include_router(mesh_federation_router)
app.include_router(mesh_workflow_router)
app.include_router(workflow_versioning_router)
app.include_router(workflow_approval_workflow_router)
app.include_router(approval_router)
app.include_router(workflow_marketplace_router)
app.include_router(workflow_analytics_router)
app.include_router(mesh_copilot_router)
app.include_router(cameras_router)
app.include_router(vision_router)
app.include_router(analytics_router)
app.include_router(tenants_router)
app.include_router(users_router)
app.include_router(audit_router)
app.include_router(system_router)


@app.get("/metrics")
async def prometheus_metrics() -> Response:
    return Response(content=generate_latest(), media_type=CONTENT_TYPE_LATEST)


@app.get("/health")
async def health_check() -> JSONResponse:
    startup_ready = bool(getattr(app.state, "startup_ready", False))
    if not startup_ready:
        return JSONResponse(
            status_code=503,
            content={
                "status": "starting",
                "service": settings.app_name,
                "environment": settings.app_env,
                "checks": {
                    "startup": "pending",
                    "database": "pending",
                    "redis": "pending",
                },
            },
        )

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
        state_redis: object = getattr(app.state, "redis", None)
        if isinstance(state_redis, aioredis.Redis):
            await cast(RedisClient, state_redis).ping()
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
                "startup": "ok",
                "database": "ok" if db_ok else "fail",
                "redis": "ok" if redis_ok else "fail",
            },
        },
    )
