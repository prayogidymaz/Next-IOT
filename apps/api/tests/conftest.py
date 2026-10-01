import os
import uuid
from collections.abc import AsyncIterator, Callable
from urllib.parse import urlparse, urlunparse

# Route pytest to an isolated DB before SQLAlchemy engine is created.
_default_sync = os.environ.get(
    "DATABASE_URL_SYNC", "postgresql://next_iot:changeme@postgres:5432/next_iot"
)
_test_db = os.environ.get("TEST_DATABASE_NAME", "next_iot_test")


def _with_db_name(url: str, db_name: str) -> str:
    parsed = urlparse(url)
    return urlunparse(parsed._replace(path=f"/{db_name}"))


_test_sync_url = _with_db_name(_default_sync, _test_db)
_test_async_url = _test_sync_url.replace("postgresql://", "postgresql+asyncpg://", 1)
os.environ["DATABASE_URL"] = _test_async_url
os.environ["DATABASE_URL_SYNC"] = _test_sync_url

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
    parsed = urlparse(_default_sync)
    return urlunparse(parsed._replace(path="/postgres"))


def _ensure_test_database() -> None:
    admin_conn = psycopg2.connect(_admin_db_url())
    admin_conn.autocommit = True
    with admin_conn.cursor() as cur:
        cur.execute("SELECT 1 FROM pg_database WHERE datname = %s", (_test_db,))
        if cur.fetchone() is None:
            cur.execute(f'CREATE DATABASE "{_test_db}"')
    admin_conn.close()


def _run_test_migrations() -> None:
    from alembic import command
    from alembic.config import Config

    cfg = Config("alembic.ini")
    cfg.set_main_option("sqlalchemy.url", _test_sync_url)
    command.upgrade(cfg, "head")


def truncate_auth_tables() -> None:
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
