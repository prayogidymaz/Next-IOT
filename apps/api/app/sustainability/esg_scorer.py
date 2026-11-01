"""Weighted ESG scoring."""

from __future__ import annotations

import uuid
from decimal import Decimal

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.sso.models import SsoConfig
from app.models.audit_log import AuditLog
from app.sustainability.models import CarbonEntry, WaterUsage


def grade_from_score(overall: Decimal) -> str:
    if overall >= Decimal("90"):
        return "A"
    if overall >= Decimal("80"):
        return "B"
    if overall >= Decimal("70"):
        return "C"
    if overall >= Decimal("60"):
        return "D"
    return "F"


async def compute_scores(db: AsyncSession, tenant_id: uuid.UUID, period_month: str) -> tuple[Decimal, Decimal, Decimal, str]:
    carbon_total = await db.scalar(
        select(func.coalesce(func.sum(CarbonEntry.co2_equivalent_kg), 0)).where(
            CarbonEntry.tenant_id == tenant_id,
            func.to_char(CarbonEntry.recorded_at, "YYYY-MM") == period_month,
        )
    )
    water_total = await db.scalar(
        select(func.coalesce(func.sum(WaterUsage.liters_used), 0)).where(
            WaterUsage.tenant_id == tenant_id,
            func.to_char(WaterUsage.recorded_at, "YYYY-MM") == period_month,
        )
    )
    audit_count = await db.scalar(
        select(func.count()).select_from(AuditLog).where(
            AuditLog.tenant_id == tenant_id,
            func.to_char(AuditLog.timestamp, "YYYY-MM") == period_month,
        )
    )
    sso_enabled = await db.scalar(
        select(func.count()).select_from(SsoConfig).where(SsoConfig.tenant_id == tenant_id, SsoConfig.enabled.is_(True))
    )
    carbon_f = float(carbon_total or 0)
    water_f = float(water_total or 0)
    env = max(Decimal("0"), Decimal("100") - Decimal(str(min(carbon_f / 10, 40))) - Decimal(str(min(water_f / 10000, 30))))
    social = Decimal("70") + Decimal(str(min(audit_count or 0, 10)))
    gov = Decimal("60") + Decimal(str(min(audit_count or 0, 15))) + (Decimal("10") if (sso_enabled or 0) > 0 else Decimal("0"))
    social = min(social, Decimal("100"))
    gov = min(gov, Decimal("100"))
    overall = env * Decimal("0.5") + social * Decimal("0.25") + gov * Decimal("0.25")
    return env.quantize(Decimal("0.01")), social.quantize(Decimal("0.01")), gov.quantize(Decimal("0.01")), grade_from_score(overall)
