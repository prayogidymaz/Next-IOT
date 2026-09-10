import os
import uuid
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
import redis.asyncio as aioredis
from httpx import ASGITransport, AsyncClient

from app.config import settings
from app.database import engine
from app.main import app


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
    with conn.cursor() as cur:
        cur.execute(
            "TRUNCATE telemetry_anomalies, device_commands, rules, telemetry_readings, device_metadata, device_credentials, devices, users, tenants RESTART IDENTITY CASCADE"
        )
    conn.close()


async def _clear_redis_keys() -> None:
    redis = aioredis.from_url(settings.redis_url, decode_responses=True)
    for pattern in (
        "refresh:*",
        "ratelimit:*",
        "provision:*",
        "device:liveness:*",
        "device:telemetry:latest:*",
        "device:alerts*",
        "hardware:*",
    ):
        keys = [k async for k in redis.scan_iter(pattern)]
        if keys:
            await redis.delete(*keys)
    await redis.delete("device:alerts", "device:alerts:history")
    await redis.aclose()


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


@pytest.fixture
async def client():
    await _clear_redis_keys()
    truncate_auth_tables()

    redis = aioredis.from_url(settings.redis_url, decode_responses=True)
    await redis.ping()
    app.state.redis = redis

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac

    await _clear_redis_keys()
    truncate_auth_tables()
    await redis.aclose()
    app.state.redis = None


@pytest.fixture
def unique_email() -> str:
    return f"admin-{uuid.uuid4().hex[:8]}@example.com"


@pytest.fixture
def unique_slug() -> str:
    return f"tenant-{uuid.uuid4().hex[:8]}"
