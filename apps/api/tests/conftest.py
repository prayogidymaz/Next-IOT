import logging
import os
import time
import uuid
from collections.abc import AsyncIterator, Callable
from urllib.parse import urlparse, urlunparse

# Pytest must not touch the live app DB/Redis or start background workers.
os.environ.setdefault("RUN_BACKGROUND_WORKERS", "false")
os.environ.setdefault("SEED_DEFAULT_ADMIN", "false")
os.environ.setdefault("SEED_DEMO_TELEMETRY", "false")
os.environ.setdefault("EMQX_API_KEY", "nextiot-api-key")
os.environ.setdefault("EMQX_API_SECRET", "nextiot-api-secret-change-in-prod")
os.environ.setdefault("TESTING", "1")
os.environ.setdefault("MQTT_SUBSCRIBER_ENABLED", "false")
os.environ.setdefault("ALARM_NOTIFICATIONS_ENABLED", "false")
os.environ.setdefault("MQTT_SUBSCRIBER_INTERNAL_PASSWORD", "next-iot-subscriber-dev-password")


def _bootstrap_test_database_env() -> tuple[str, str]:
    sync_base = os.environ.get(
        "DATABASE_URL_SYNC",
        "postgresql://next_iot:changeme@postgres:5432/next_iot",
    )
    explicit_test = os.environ.get("DATABASE_URL_TEST", "").strip()
    if explicit_test:
        test_async = explicit_test
        test_sync = explicit_test.replace("postgresql+asyncpg://", "postgresql://", 1)
    else:
        test_name = os.environ.get("TEST_DATABASE_NAME", "").strip()
        if not test_name:
            base_db = urlparse(sync_base).path.lstrip("/").split("/", 1)[0] or "next_iot"
            test_name = base_db if base_db.endswith("_test") else f"{base_db}_test"
        parsed = urlparse(sync_base)
        test_sync = urlunparse(parsed._replace(path=f"/{test_name}"))
        test_async = test_sync.replace("postgresql://", "postgresql+asyncpg://", 1)
    os.environ["DATABASE_URL"] = test_async
    os.environ["DATABASE_URL_SYNC"] = test_sync
    return test_sync, test_async


_test_sync_url, _test_async_url = _bootstrap_test_database_env()

import psycopg2
import pytest
from app.config import settings
from app.database import async_session, engine
from app.deps import get_redis
from app.main import app
from app.mqtt_publisher.noop import NoopMqttPublisher
from app.mesh.publisher import init_mesh_publisher
from app.mesh.workflow_executor import init_mesh_workflow_executor
from app.mesh.workflow_registry import reload_workflows
from app.rules.executor import init_rule_executor
from app.types.redis_client import RedisClient, close_redis, redis_from_url
from fastapi import Request
from httpx import ASGITransport, AsyncClient


def _admin_db_url() -> str:
    return settings.admin_postgres_url()


def _ensure_test_database() -> None:
    test_db = settings.database_name_from_url(_test_sync_url)
    settings.assert_test_database_name(test_db)
    admin_conn = psycopg2.connect(_admin_db_url())
    admin_conn.autocommit = True
    with admin_conn.cursor() as cur:
        cur.execute("SELECT 1 FROM pg_database WHERE datname = %s", (test_db,))
        if cur.fetchone() is None:
            cur.execute(f'CREATE DATABASE "{test_db}"')
    admin_conn.close()


def _run_test_migrations() -> None:
    from alembic import command
    from alembic.config import Config

    settings.assert_test_database_url(_test_sync_url)
    cfg = Config("alembic.ini")
    cfg.set_main_option("sqlalchemy.url", _test_sync_url)
    command.upgrade(cfg, "head")


def seed_subscription_plans_sync() -> None:
    import json
    import uuid

    from app.billing.plan_definitions import plan_seed_rows

    conn = psycopg2.connect(_test_sync_url)
    conn.autocommit = True
    with conn.cursor() as cur:
        cur.execute("SELECT 1 FROM subscription_plans LIMIT 1")
        if cur.fetchone() is not None:
            conn.close()
            return
        for row in plan_seed_rows():
            code_raw = row.get("code")
            if not isinstance(code_raw, str):
                continue
            limits_raw = row.get("limits")
            limits_obj = limits_raw if isinstance(limits_raw, dict) else {}
            cur.execute(
                """
                INSERT INTO subscription_plans
                (id, code, name, description, monthly_price_idr, yearly_price_idr, limits, is_active, display_order)
                VALUES (%s, %s, %s, %s, %s, %s, %s::jsonb, true, %s)
                """,
                (
                    str(uuid.uuid4()),
                    code_raw,
                    str(row.get("name", code_raw)),
                    row.get("description"),
                    row.get("monthly_price_idr"),
                    row.get("yearly_price_idr"),
                    json.dumps(limits_obj),
                    int(row.get("display_order", 0)),
                ),
            )
    conn.close()


_AUTH_TRUNCATE_TABLES: tuple[str, ...] = (
    "super_admin_actions",
    "invoices",
    "tenant_usage_daily",
    "tenant_subscriptions",
    "payment_methods",
    "subscription_plans",
    "audit_logs",
    "ota_device_rollouts",
    "firmware_releases",
    "automation_pipelines",
    "rule_execution_log",
    "notification_log",
    "notification_rules",
    "notification_channels",
    "alarm_history",
    "alarms",
    "sar_incidents",
    "telemetry_anomalies",
    "geofence_zones",
    "vision_feedback",
    "vision_detections",
    "vision_tenant_config",
    "federation_events_log",
    "federation_peers",
    "edge_device_tokens",
    "firmware_versions",
    "anomaly_events",
    "yield_forecasts",
    "optimization_reports",
    "device_rpc_requests",
    "device_attributes",
    "device_commands",
    "rules",
    "telemetry_readings",
    "device_metadata",
    "device_credentials",
    "device_claim_tokens",
    "devices",
    "device_profiles",
    "tenant_memberships",
    "users",
    "tenants",
)


def truncate_auth_tables() -> None:
    """Reset tenant-scoped tables between tests.

    Uses TRUNCATE CASCADE with lock/statement timeouts. Does NOT use
    pg_terminate_backend (would kill the app's async pool mid-flight).
    Fixture callers must ``await engine.dispose()`` before calling this
    so the async pool releases connections first.
    """
    log = logging.getLogger(__name__)
    settings.assert_test_database_url(_test_sync_url)
    tables_csv = ", ".join(_AUTH_TRUNCATE_TABLES)
    truncate_sql = f"TRUNCATE {tables_csv} RESTART IDENTITY CASCADE"
    for attempt in range(3):
        conn = psycopg2.connect(_test_sync_url)
        conn.autocommit = True
        try:
            with conn.cursor() as cur:
                cur.execute("SET lock_timeout = '5s'")
                cur.execute("SET statement_timeout = '15s'")
                cur.execute(truncate_sql)
            return
        except psycopg2.OperationalError as exc:
            log.warning(
                "truncate_auth_tables attempt %s/3 failed: %s",
                attempt + 1,
                exc,
            )
            time.sleep(0.25 * (attempt + 1))
        finally:
            conn.close()
    log.warning("truncate_auth_tables gave up after 3 attempts")


def _override_get_redis(redis: RedisClient) -> Callable[[Request], RedisClient]:
    def _getter(_request: Request) -> RedisClient:
        return redis

    return _getter


@pytest.fixture(scope="session", autouse=True)
def _prepare_test_database():
    assert settings.database_url == _test_async_url
    assert settings.database_url_sync == _test_sync_url
    assert not settings.run_background_workers
    _ensure_test_database()
    _run_test_migrations()
    seed_subscription_plans_sync()
    yield


@pytest.fixture(autouse=True)
def _disable_alarm_notification_tasks(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(settings, "alarm_notifications_enabled", False)


@pytest.fixture(autouse=True)
async def reset_async_engine():
    await engine.dispose()
    yield
    await engine.dispose()


async def _flush_test_redis(redis: RedisClient) -> None:
    settings.assert_test_redis_isolated()
    await redis.flushdb()


@pytest.fixture
async def test_redis() -> AsyncIterator[RedisClient]:
    redis = redis_from_url(settings.redis_url_for_tests())
    await _flush_test_redis(redis)
    yield redis
    await _flush_test_redis(redis)
    await close_redis(redis)


@pytest.fixture
async def client(test_redis: RedisClient) -> AsyncIterator[AsyncClient]:
    truncate_auth_tables()
    seed_subscription_plans_sync()

    publisher = NoopMqttPublisher()
    app.state.redis = test_redis
    app.state.mqtt_publisher = publisher
    mesh_publisher = init_mesh_publisher(test_redis, publisher)
    init_mesh_workflow_executor(test_redis, mesh_publisher, publisher)
    rule_executor = init_rule_executor(test_redis, publisher)
    await rule_executor.startup()
    app.state.rule_executor = rule_executor
    async with async_session() as session:
        await reload_workflows(session)
        await session.commit()
    app.state.startup_ready = True
    app.dependency_overrides[get_redis] = _override_get_redis(test_redis)

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac

    app.dependency_overrides.pop(get_redis, None)
    app.state.redis = None
    await engine.dispose()
    truncate_auth_tables()


@pytest.fixture
def unique_email() -> str:
    return f"admin-{uuid.uuid4().hex[:8]}@example.com"


@pytest.fixture
def unique_slug() -> str:
    return f"tenant-{uuid.uuid4().hex[:8]}"
