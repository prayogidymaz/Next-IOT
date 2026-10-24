"""Firebase Cloud Messaging push client."""

from __future__ import annotations

import base64
import json
import logging
from dataclasses import dataclass

from app.config import settings
from app.types.json_types import JsonObject

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class FcmSendResult:
    success: bool
    unregistered: bool = False
    error: str | None = None


class FcmPushClient:
    """Send FCM messages via Firebase Admin SDK when configured."""

    def __init__(self) -> None:
        self._initialized = False

    def _ensure_firebase(self) -> bool:
        if self._initialized:
            return True
        if not settings.notification_fcm_enabled:
            return False
        if not settings.fcm_project_id or not settings.fcm_private_key_json_b64:
            return False
        try:
            import firebase_admin
            from firebase_admin import credentials

            try:
                firebase_admin.get_app()
                self._initialized = True
                return True
            except ValueError:
                pass
            raw = base64.b64decode(settings.fcm_private_key_json_b64)
            service_account = json.loads(raw.decode("utf-8"))
            cred = credentials.Certificate(service_account)
            firebase_admin.initialize_app(cred, {"projectId": settings.fcm_project_id})
            self._initialized = True
            return True
        except Exception:
            logger.exception("FCM firebase_admin init failed")
            return False

    async def send(
        self,
        token: str,
        title: str,
        body: str,
        data: JsonObject | None = None,
    ) -> FcmSendResult:
        if not settings.notification_fcm_enabled:
            return FcmSendResult(success=True)
        if not self._ensure_firebase():
            return FcmSendResult(success=False, error="FCM not configured")
        try:
            from firebase_admin import messaging

            message = messaging.Message(
                notification=messaging.Notification(title=title, body=body),
                data={str(k): str(v) for k, v in (data or {}).items()},
                token=token,
            )
            messaging.send(message)
            return FcmSendResult(success=True)
        except Exception as exc:
            error_text = str(exc)
            unregistered = "404" in error_text or "registration-token-not-registered" in error_text.lower()
            return FcmSendResult(success=False, unregistered=unregistered, error=error_text)


_default_client = FcmPushClient()


def get_fcm_push_client() -> FcmPushClient:
    return _default_client
