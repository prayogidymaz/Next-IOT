"""Resolve channel type to provider implementation."""

from __future__ import annotations

from app.notifications.providers.channel_base import ChannelProvider
from app.notifications.providers.email_smtp import EmailSmtpProvider
from app.notifications.providers.fcm import FcmProvider
from app.notifications.providers.fonnte import FonnteProvider
from app.notifications.providers.sms_twilio import TwilioSmsProvider
from app.notifications.providers.telegram_channel import TelegramChannelProvider

_PROVIDERS: dict[str, ChannelProvider] = {
    "whatsapp": FonnteProvider(),
    "telegram": TelegramChannelProvider(),
    "fcm": FcmProvider(),
    "email": EmailSmtpProvider(),
    "sms": TwilioSmsProvider(),
}


def provider_for(channel_type: str) -> ChannelProvider | None:
    return _PROVIDERS.get(channel_type)
