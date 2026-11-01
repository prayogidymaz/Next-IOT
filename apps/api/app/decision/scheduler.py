"""Periodic recommendation generation tick."""

from __future__ import annotations

import asyncio
import logging

from sqlalchemy import select

from app.database import async_session
from app.decision.recommender import generate_recommendations
from app.models.user import User

logger = logging.getLogger(__name__)


async def decision_tick_loop(stop_event: asyncio.Event) -> None:
    while not stop_event.is_set():
        try:
            async with async_session() as db:
                users = await db.scalars(select(User).limit(50))
                for user_row in users.all():
                    from app.auth.context import CurrentUser
                    from app.auth.tiering import SecurityTier

                    cu = CurrentUser(
                        user_id=user_row.id,
                        tenant_id=user_row.tenant_id,
                        email=user_row.email,
                        role=user_row.role,
                        security_tier=SecurityTier.FREE,
                    )
                    await generate_recommendations(db, cu)
        except Exception:
            logger.exception("decision tick failed")
        try:
            await asyncio.wait_for(stop_event.wait(), timeout=86400.0)
        except asyncio.TimeoutError:
            continue
