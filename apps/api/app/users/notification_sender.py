"""Send mobile push notifications via Expo Push API."""

from __future__ import annotations

import logging
import uuid

import httpx
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.types.json_types import JsonObject
from app.users.push_notification import UserPushToken

logger = logging.getLogger(__name__)

EXPO_PUSH_URL = "https://exp.host/--/api/v2/push/send"


async def send_push(
    db: AsyncSession,
    user_id: uuid.UUID,
    title: str,
    body: str,
    data_json: JsonObject | None = None,
) -> int:
    """Deliver push to all registered Expo tokens for user. Returns send count."""
    tokens = await db.scalars(select(UserPushToken.token).where(UserPushToken.user_id == user_id))
    token_list = list(tokens.all())
    if not token_list:
        return 0

    messages = [
        {
            "to": token,
            "title": title,
            "body": body,
            "data": data_json or {},
            "sound": "default",
        }
        for token in token_list
    ]
    async with httpx.AsyncClient(timeout=10.0) as client:
        response = await client.post(EXPO_PUSH_URL, json=messages)
        if response.status_code >= 400:
            logger.warning("Expo push failed status=%s body=%s", response.status_code, response.text[:200])
            return 0
    return len(token_list)
