"""Tier-based telemetry retention (Timescale compression + scheduled DELETE sweeps)."""

from __future__ import annotations

import asyncio
import logging
from datetime import UTC, datetime, timedelta

from sqlalchemy import delete, select, text
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.tiering import SecurityTier, parse_tier
from app.config import settings
from app.database import async_session
from app.models.telemetry_reading import TelemetryReading
from app.models.tenant import Tenant

logger = logging.getLogger(__name__)

_RETENTION_LOOP_SECONDS = 86_400.0


def retention_days_for_tier(tier: SecurityTier) -> int:
    if tier == SecurityTier.FREE:
        return settings.telemetry_retention_free_days
    if tier == SecurityTier.PRO:
        return settings.telemetry_retention_pro_days
    return settings.telemetry_retention_enterprise_days


def global_retention_policy_sql(retention_days: int) -> str:
    """SQL for Timescale global retention safety net (enterprise max tier)."""
    return (
        "SELECT add_retention_policy("
        "'telemetry_readings', "
        f"drop_after => INTERVAL '{retention_days} days', "
        "if_not_exists => true"
        ")"
    )


def tenant_retention_delete_sql() -> str:
    """Documented shape for per-tenant DELETE (ORM used at runtime)."""
    return (
        "DELETE FROM telemetry_readings "
        "WHERE tenant_id = :tenant_id AND recorded_at < :cutoff"
    )


async def apply_retention_policies(db: AsyncSession) -> None:
    """Global Timescale retention at enterprise horizon; tier-specific pruning via sweep."""
    sql = global_retention_policy_sql(settings.telemetry_retention_enterprise_days)
    await db.execute(text(sql))
    await db.commit()


async def sweep_tenant_retention(db: AsyncSession) -> int:
    """Delete readings older than each tenant's tier window (pragmatic per-tenant retention)."""
    tenants = await db.scalars(select(Tenant))
    removed = 0
    now = datetime.now(UTC)
    for tenant in tenants.all():
        tier = parse_tier(tenant.security_tier)
        days = retention_days_for_tier(tier)
        cutoff = now - timedelta(days=days)
        result = await db.execute(
            delete(TelemetryReading).where(
                TelemetryReading.tenant_id == tenant.id,
                TelemetryReading.recorded_at < cutoff,
            )
        )
        if result.rowcount is not None:
            removed += result.rowcount
    await db.commit()
    return removed


async def run_retention_maintenance() -> None:
    async with async_session() as db:
        await apply_retention_policies(db)
        deleted = await sweep_tenant_retention(db)
        if deleted:
            logger.info("Telemetry retention sweep deleted %s row(s)", deleted)


async def telemetry_retention_loop(stop_event: asyncio.Event) -> None:
    """Daily retention maintenance; skipped when run_background_workers is false."""
    while not stop_event.is_set():
        try:
            await run_retention_maintenance()
        except Exception:
            logger.exception("Telemetry retention maintenance failed")
        try:
            await asyncio.wait_for(stop_event.wait(), timeout=_RETENTION_LOOP_SECONDS)
            return
        except TimeoutError:
            continue
