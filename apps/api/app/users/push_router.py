"""Push token routes under /api/v1/users."""

from __future__ import annotations

from typing import Literal

from fastapi import APIRouter, Response, status
from pydantic import BaseModel, Field
from sqlalchemy import select

from app.auth.dependencies import RequireAuth
from app.deps import DbSession
from app.users.notification_sender import send_push
from app.users.push_notification import UserPushToken

router = APIRouter(prefix="/api/v1/users", tags=["users-push"])


class PushTokenBody(BaseModel):
    token: str = Field(min_length=8)
    platform: Literal["ios", "android"]


@router.post("/me/push-token", status_code=status.HTTP_204_NO_CONTENT, response_class=Response)
async def register_push_token(user: RequireAuth, db: DbSession, body: PushTokenBody) -> Response:
    existing = await db.scalar(
        select(UserPushToken).where(
            UserPushToken.user_id == user.user_id,
            UserPushToken.token == body.token,
        )
    )
    if existing is None:
        db.add(
            UserPushToken(
                user_id=user.user_id,
                token=body.token,
                platform=body.platform,
            )
        )
        await db.flush()
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.post("/me/push-token/test", status_code=status.HTTP_204_NO_CONTENT, response_class=Response)
async def test_push_token(user: RequireAuth, db: DbSession) -> Response:
    await send_push(db, user.user_id, "Next-IOT", "Test notification from field app", {"type": "test"})
    return Response(status_code=status.HTTP_204_NO_CONTENT)
