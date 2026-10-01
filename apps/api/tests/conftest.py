import os
import uuid
from collections.abc import AsyncIterator, Callable
from urllib.parse import urlparse, urlunparse

# Pytest must not touch the live app DB/Redis or start background workers.
os.environ.setdefault("RUN_BACKGROUND_WORKERS", "false")
os.environ.setdefault("SEED_DEFAULT_ADMIN", "false")
os.environ.setdefault("SEED_DEMO_TELEMETRY", "false")


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
from app.database import engine
from app.deps import get_redis
from app.main import app
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


def truncate_auth_tables() -> None:
    settings.assert_test_database_url(_test_sync_url)
    conn = psycopg2.connect(_test_sync_url)
    conn.autocommit = True
    truncate_sql = (
        "TRUNCATE audit_logs, ota_device_rollouts, firmware_releases, automation_pipelines, "
        "sar_incidents, telemetry_anomalies, geofence_zones, device_commands, rules, "
        "telemetry_readings, device_metadata, device_credentials, devices, tenant_memberships, "
        "users, tenants RESTART IDENTITY CASCADE"
    )
    with conn.cursor() as cur:
        cur.execute(truncate_sql)
    conn.close()


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
    yield


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

    app.state.redis = test_redis
    app.dependency_overrides[get_redis] = _override_get_redis(test_redis)

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac

    app.dependency_overrides.pop(get_redis, None)
    app.state.redis = None
    truncate_auth_tables()


@pytest.fixture
def unique_email() -> str:
    return f"admin-{uuid.uuid4().hex[:8]}@example.com"


@pytest.fixture
def unique_slug() -> str:
    return f"tenant-{uuid.uuid4().hex[:8]}"
