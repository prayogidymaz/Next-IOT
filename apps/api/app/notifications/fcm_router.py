"""FCM token registration for mobile and edge clients."""

from __future__ import annotations

from fastapi import APIRouter, Query, Response, status

from app.auth.dependencies import RequireAuth
from app.deps import DbSession
from app.notifications.fcm_schemas import FcmRegisterRequest, FcmTokenView
from app.notifications.fcm_token_service import list_user_fcm_tokens, register_fcm_token, unregister_fcm_token

router = APIRouter(prefix="/api/v1/notifications/fcm", tags=["notifications-fcm"])


@router.post("/register", response_model=FcmTokenView, status_code=status.HTTP_201_CREATED)
async def post_fcm_register(
    user: RequireAuth,
    db: DbSession,
    payload: FcmRegisterRequest,
) -> FcmTokenView:
    row = await register_fcm_token(db, user, payload.token, payload.device_type)
    return FcmTokenView(
        id=row.id,
        token=row.token,
        device_type=row.device_type,
        last_seen_at=row.last_seen_at,
        created_at=row.created_at,
    )


@router.delete("/unregister", status_code=status.HTTP_204_NO_CONTENT, response_class=Response)
async def delete_fcm_unregister(
    user: RequireAuth,
    db: DbSession,
    token: str = Query(min_length=8, max_length=512),
) -> Response:
    await unregister_fcm_token(db, user, token)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.get("/tokens", response_model=list[FcmTokenView])
async def get_fcm_tokens(user: RequireAuth, db: DbSession) -> list[FcmTokenView]:
    rows = await list_user_fcm_tokens(db, user)
    return [
        FcmTokenView(
            id=row.id,
            token=row.token,
            device_type=row.device_type,
            last_seen_at=row.last_seen_at,
            created_at=row.created_at,
        )
        for row in rows
    ]
