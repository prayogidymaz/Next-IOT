"""SMTP email channel provider."""

from __future__ import annotations

from email.message import EmailMessage

from app.config import settings
from app.notifications.providers.channel_base import ProviderResult
from app.types.json_types import JsonObject, as_json_str


class EmailSmtpProvider:
    channel_type = "email"

    async def send(
        self,
        config: JsonObject,
        title: str,
        message: str,
        severity: str,
    ) -> ProviderResult:
        address = as_json_str(config.get("address"))
        if not address:
            return ProviderResult(success=False, error="missing email address in channel config")
        if not settings.notification_email_smtp_host:
            return ProviderResult(
                success=True,
                response={"mock": True, "provider": "email", "to": address},
                delivered=True,
            )
        msg = EmailMessage()
        msg["From"] = settings.notification_email_from
        msg["To"] = address
        msg["Subject"] = f"[{severity.upper()}] {title}"
        msg.set_content(message)
        import aiosmtplib

        await aiosmtplib.send(
            msg,
            hostname=settings.notification_email_smtp_host,
            port=settings.notification_email_smtp_port,
            username=settings.notification_email_smtp_user or None,
            password=settings.notification_email_smtp_password or None,
            start_tls=True,
        )
        return ProviderResult(success=True, response={"sent": True}, delivered=True)
