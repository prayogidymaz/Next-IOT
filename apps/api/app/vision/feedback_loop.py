"""False-positive feedback and adaptive confidence thresholds."""

from __future__ import annotations

import uuid
from datetime import UTC, datetime

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.vision.models import VisionFeedback, VisionTenantConfig


def compute_adjusted_threshold(current: float, false_positive_rate: float) -> float:
    if false_positive_rate > 0.15:
        return min(0.95, current + 0.05)
    if false_positive_rate < 0.05:
        return max(0.45, current - 0.03)
    return current


class FalsePositiveFeedback:
    ADJUSTMENT_WINDOW = 100

    async def submit(
        self,
        db: AsyncSession,
        detection_id: uuid.UUID,
        verdict: str,
        notes: str,
        verified_by: uuid.UUID,
        tenant_id: uuid.UUID,
    ) -> VisionFeedback:
        row = VisionFeedback(
            detection_id=detection_id,
            tenant_id=tenant_id,
            verdict=verdict,
            notes=notes,
            verified_by=verified_by,
            verified_at=datetime.now(tz=UTC),
        )
        db.add(row)
        await db.flush()
        await self._maybe_adjust_threshold(db, tenant_id)
        return row

    async def _maybe_adjust_threshold(self, db: AsyncSession, tenant_id: uuid.UUID) -> None:
        count = await db.scalar(
            select(func.count())
            .select_from(VisionFeedback)
            .where(VisionFeedback.tenant_id == tenant_id)
        )
        if count is None or count < self.ADJUSTMENT_WINDOW or count % self.ADJUSTMENT_WINDOW != 0:
            return
        false_count = await db.scalar(
            select(func.count())
            .select_from(VisionFeedback)
            .where(
                VisionFeedback.tenant_id == tenant_id,
                VisionFeedback.verdict == "false_positive",
            )
        )
        false_count = false_count or 0
        fp_rate = false_count / float(self.ADJUSTMENT_WINDOW)
        config = await db.scalar(
            select(VisionTenantConfig).where(VisionTenantConfig.tenant_id == tenant_id)
        )
        if config is None:
            config = VisionTenantConfig(tenant_id=tenant_id)
            db.add(config)
        config.confidence_threshold = compute_adjusted_threshold(float(config.confidence_threshold), fp_rate)
