from datetime import UTC, datetime

from fastapi import APIRouter

from app.auth.dependencies import RequireTenantAdmin
from app.notifications.dispatcher import NotificationDispatcher, build_notifiers
from app.notifications.schemas import (
    NotificationTestRequest,
    NotificationTestResponse,
    ProviderDispatchResult,
)

router = APIRouter(prefix="/api/v1/notifications", tags=["notifications"])


def _build_test_alert(user: RequireTenantAdmin, message: str) -> dict:
    return {
        "event": "notification.test",
        "device_id": "00000000-0000-0000-0000-000000000000",
        "tenant_id": str(user.tenant_id),
        "metric": "test",
        "operator": "eq",
        "threshold": 0,
        "actual_value": 1,
        "action_type": "alert",
        "reading_id": "00000000-0000-0000-0000-000000000000",
        "message": message,
        "timestamp": datetime.now(UTC).isoformat(),
    }


@router.post("/test", response_model=NotificationTestResponse)
async def test_notification_dispatch(
    payload: NotificationTestRequest,
    user: RequireTenantAdmin,
):
    """Trigger a test notification through configured providers (tenant_admin+)."""
    channels = payload.channels
    use_all = "all" in channels
    include_telegram = use_all or "telegram" in channels
    include_webhook = use_all or "webhook" in channels

    alert = _build_test_alert(user, payload.message)
    dispatcher = NotificationDispatcher(
        notifiers=build_notifiers(
            include_telegram=include_telegram,
            include_webhook=include_webhook,
        )
    )
    results = await dispatcher.dispatch(alert)

    return NotificationTestResponse(
        alert=alert,
        results=[
            ProviderDispatchResult(
                provider=r.provider,
                success=r.success,
                attempts=r.attempts,
                error=r.error,
            )
            for r in results
        ],
    )
