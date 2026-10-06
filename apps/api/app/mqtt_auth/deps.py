"""Shared secret for EMQX → API webhooks."""

from __future__ import annotations

from typing import Annotated

from app.config import settings
from fastapi import Header, HTTPException, status


async def require_mqtt_webhook_secret(
    x_internal_secret: Annotated[str | None, Header(alias="X-Internal-Secret")] = None,
) -> None:
    expected = settings.mqtt_webhook_shared_secret.strip()
    if not expected:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="MQTT webhook secret is not configured",
        )
    if x_internal_secret != expected:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Invalid webhook secret")


MqttWebhookSecret = Annotated[None, require_mqtt_webhook_secret]
