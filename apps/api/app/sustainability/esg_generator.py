"""Monthly ESG scorecard computation."""

from __future__ import annotations

import uuid

from sqlalchemy.ext.asyncio import AsyncSession

from app.sustainability.esg_scorer import compute_scores
from app.sustainability.models import EsgScorecard


async def generate_scorecard(db: AsyncSession, tenant_id: uuid.UUID, period_month: str) -> EsgScorecard:
    env, social, gov, grade = await compute_scores(db, tenant_id, period_month)
    row = EsgScorecard(
        tenant_id=tenant_id,
        period_month=period_month,
        environmental_score=env,
        social_score=social,
        governance_score=gov,
        overall_grade=grade,
        report_pdf_url=None,
    )
    db.add(row)
    await db.flush()
    row.report_pdf_url = f"/api/v1/sustainability/esg/{row.id}/pdf"
    await db.commit()
    await db.refresh(row)
    return row
