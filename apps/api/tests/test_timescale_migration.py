"""Timescale hypertable + migration 015 integration (requires TimescaleDB postgres image)."""

from __future__ import annotations

import psycopg2
import pytest
from alembic import command
from alembic.config import Config
from app.database import engine
from sqlalchemy import text

from tests.conftest import _test_sync_url


def _timescale_installed(sync_url: str) -> bool:
    conn = psycopg2.connect(sync_url)
    conn.autocommit = True
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT 1 FROM pg_available_extensions WHERE name = 'timescaledb'")
            return cur.fetchone() is not None
    finally:
        conn.close()


@pytest.fixture(scope="module")
def require_timescale() -> None:
    if not _timescale_installed(_test_sync_url):
        pytest.skip("TimescaleDB extension not available on this Postgres instance")


@pytest.fixture(scope="session", autouse=True)
def _alembic_015_roundtrip_after_session(request: pytest.FixtureRequest) -> None:
    """Run 014→015→014→015 after all tests to avoid deadlocks with per-test TRUNCATE."""

    if not _timescale_installed(_test_sync_url):
        yield
        return

    yield

    cfg = Config("alembic.ini")
    cfg.set_main_option("sqlalchemy.url", _test_sync_url)

    conn = psycopg2.connect(_test_sync_url)
    conn.autocommit = True
    with conn.cursor() as cur:
        cur.execute("SELECT COUNT(*) FROM telemetry_readings")
        before_row = cur.fetchone()
        before = before_row[0] if before_row is not None else 0
    conn.close()

    try:
        command.downgrade(cfg, "014")
        command.upgrade(cfg, "015")

        conn = psycopg2.connect(_test_sync_url)
        conn.autocommit = True
        with conn.cursor() as cur:
            cur.execute("SELECT COUNT(*) FROM telemetry_readings")
            after_row = cur.fetchone()
            after = after_row[0] if after_row is not None else 0
            cur.execute(
                """
                SELECT COUNT(*)::int FROM timescaledb_information.hypertables
                WHERE hypertable_name = 'telemetry_readings'
                """
            )
            ht_row = cur.fetchone()
            hypertable_count = ht_row[0] if ht_row is not None else 0
        conn.close()

        assert after == before
        assert hypertable_count == 1
    finally:
        command.upgrade(cfg, "head")


@pytest.mark.asyncio
async def test_telemetry_readings_hypertable_exists(require_timescale: None) -> None:
    async with engine.connect() as conn:
        count = await conn.scalar(
            text(
                """
                SELECT COUNT(*)::int FROM timescaledb_information.hypertables
                WHERE hypertable_schema = 'public' AND hypertable_name = 'telemetry_readings'
                """
            )
        )
    assert count == 1


@pytest.mark.asyncio
async def test_telemetry_compression_settings(require_timescale: None) -> None:
    async with engine.connect() as conn:
        enabled = await conn.scalar(
            text(
                """
                SELECT compression_enabled::int FROM timescaledb_information.hypertables
                WHERE hypertable_schema = 'public' AND hypertable_name = 'telemetry_readings'
                """
            )
        )
    assert enabled == 1


def test_alembic_015_roundtrip_scheduled(require_timescale: None) -> None:
    """Row-preserving downgrade/upgrade runs in session finalizer (see autouse fixture)."""
    assert _timescale_installed(_test_sync_url)
