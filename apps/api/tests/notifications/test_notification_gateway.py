"""Notification gateway tests."""

from __future__ import annotations

import uuid
from unittest.mock import AsyncMock, patch

import pytest
from app.models.alarm import Alarm, AlarmStatus
from app.models.notification_gateway import NotificationLog
from app.notifications.gateway_dispatcher import alarm_matches_filter, dispatch_alarm_notifications
from app.notifications.providers.channel_base import ProviderResult
from app.notifications.providers.email_smtp import EmailSmtpProvider
from app.notifications.providers.fonnte import FonnteProvider
from app.notifications.providers.telegram_channel import TelegramChannelProvider
from httpx import AsyncClient
from sqlalchemy import select

PASSWORD = "SecurePass123!"


async def _register(client: AsyncClient, slug: str, email: str) -> tuple[str, uuid.UUID]:
    reg = await client.post(
        "/auth/register",
        json={
            "tenant_name": f"T {slug}",
            "tenant_slug": slug,
            "email": email,
            "password": PASSWORD,
        },
    )
    assert reg.status_code == 201
    body = reg.json()
    return body["tokens"]["access_token"], uuid.UUID(body["tenant_id"])


async def _token(client: AsyncClient, slug: str, email: str) -> str:
    token, _ = await _register(client, slug, email)
    return token


@pytest.mark.asyncio
async def test_notification_channel_crud(client: AsyncClient, unique_slug: str, unique_email: str) -> None:
    token = await _token(client, unique_slug, unique_email)
    create = await client.post(
        "/api/v1/notification-channels",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "channel_type": "email",
            "name": "Admin Email",
            "config": {"address": "test@example.com"},
        },
    )
    assert create.status_code == 201
    listed = await client.get(
        "/api/v1/notification-channels",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert len(listed.json()) >= 1


def test_notification_rule_matches_alarm_filter() -> None:
    alarm = Alarm(
        tenant_id=uuid.uuid4(),
        alarm_type="test",
        severity="critical",
        status=AlarmStatus.ACTIVE,
        title="t",
        fingerprint="fp",
        occurred_at=__import__("datetime").datetime.now(__import__("datetime").UTC),
    )
    assert alarm_matches_filter(alarm, {"severity": ["critical", "major"]}) is True
    assert alarm_matches_filter(alarm, {"severity": ["minor"]}) is False


@pytest.mark.asyncio
async def test_dispatcher_throttle_prevents_spam(test_redis) -> None:
    from app.notifications.gateway_dispatcher import _is_throttled, _mark_throttle

    cid = uuid.uuid4()
    fp = "abc"
    await _mark_throttle(test_redis, cid, fp, 60)
    assert await _is_throttled(test_redis, cid, fp) is True


@pytest.mark.asyncio
async def test_dispatcher_sends_to_multiple_channels(
    client: AsyncClient, test_redis, unique_slug: str, unique_email: str
) -> None:
    from datetime import UTC, datetime

    from app.database import async_session
    from app.models.notification_gateway import NotificationChannel, NotificationRule

    _, tenant_id = await _register(client, unique_slug, unique_email)
    async with async_session() as db:
        alarm = Alarm(
            tenant_id=tenant_id,
            alarm_type="test",
            severity="critical",
            status=AlarmStatus.ACTIVE,
            title="Notify",
            fingerprint=f"fp-{uuid.uuid4().hex}",
            occurred_at=datetime.now(UTC),
        )
        ch1 = NotificationChannel(
            tenant_id=tenant_id,
            channel_type="email",
            name="E1",
            config={"address": "a@b.com"},
        )
        ch2 = NotificationChannel(
            tenant_id=tenant_id,
            channel_type="telegram",
            name="T1",
            config={},
        )
        db.add_all([alarm, ch1, ch2])
        await db.flush()
        db.add(
            NotificationRule(
                tenant_id=tenant_id,
                name="All",
                alarm_filter={"severity": ["critical"]},
                channel_ids=[ch1.id, ch2.id],
                throttle_seconds=1,
            )
        )
        await db.flush()
        await dispatch_alarm_notifications(db, test_redis, alarm.id)
        await db.commit()
        logs = list(
            await db.scalars(select(NotificationLog).where(NotificationLog.alarm_id == alarm.id))
        )
    assert len(logs) >= 2


@pytest.mark.asyncio
async def test_provider_fonnte_mock_success() -> None:
    result = await FonnteProvider().send({}, "T", "M", "critical")
    assert result.success is True


@pytest.mark.asyncio
async def test_provider_telegram_mock_success() -> None:
    result = await TelegramChannelProvider().send({}, "T", "M", "warning")
    assert result.success is True


@pytest.mark.asyncio
async def test_provider_email_mock_success() -> None:
    result = await EmailSmtpProvider().send({"address": "x@y.com"}, "T", "M", "info")
    assert result.success is True


@pytest.mark.asyncio
async def test_provider_retry_on_failure(
    client: AsyncClient, test_redis, unique_slug: str, unique_email: str
) -> None:
    from app.database import async_session
    from app.models.notification_gateway import NotificationChannel
    from app.notifications.gateway_dispatcher import _send_with_retry

    provider = AsyncMock()
    provider.channel_type = "email"
    provider.send = AsyncMock(
        side_effect=[
            ProviderResult(success=False, error="fail"),
            ProviderResult(success=True, delivered=True),
        ]
    )
    _, tenant_id = await _register(client, unique_slug, unique_email)
    with patch("app.notifications.gateway_dispatcher.provider_for", return_value=provider), patch(
        "app.notifications.gateway_dispatcher.asyncio.sleep", new_callable=AsyncMock
    ):
        async with async_session() as db:
            alarm = Alarm(
                tenant_id=tenant_id,
                alarm_type="t",
                severity="info",
                status=AlarmStatus.ACTIVE,
                title="t",
                fingerprint="fp2",
                occurred_at=__import__("datetime").datetime.now(__import__("datetime").UTC),
            )
            db.add(alarm)
            await db.flush()
            channel = NotificationChannel(
                tenant_id=alarm.tenant_id,
                channel_type="email",
                name="c",
                config={"address": "a@b.com"},
            )
            db.add(channel)
            await db.flush()
            await _send_with_retry(db, alarm=alarm, channel=channel, throttle_seconds=1, redis=test_redis)
            log = await db.scalar(
                select(NotificationLog).where(NotificationLog.alarm_id == alarm.id)
            )
            assert log is not None
            assert log.status in {"sent", "delivered"}


@pytest.mark.asyncio
async def test_notification_log_tracks_status(
    client: AsyncClient, test_redis, unique_slug: str, unique_email: str
) -> None:
    from datetime import UTC, datetime

    from app.database import async_session
    from app.models.notification_gateway import NotificationChannel, NotificationRule

    _, tenant_id = await _register(client, unique_slug, unique_email)
    async with async_session() as db:
        alarm = Alarm(
            tenant_id=tenant_id,
            alarm_type="t",
            severity="info",
            status=AlarmStatus.ACTIVE,
            title="Log",
            fingerprint=f"fp-{uuid.uuid4().hex}",
            occurred_at=datetime.now(UTC),
        )
        channel = NotificationChannel(
            tenant_id=tenant_id,
            channel_type="email",
            name="L",
            config={"address": "l@x.com"},
        )
        db.add_all([alarm, channel])
        await db.flush()
        db.add(
            NotificationRule(
                tenant_id=tenant_id,
                name="R",
                alarm_filter={},
                channel_ids=[channel.id],
                throttle_seconds=1,
            )
        )
        await db.flush()
        await dispatch_alarm_notifications(db, test_redis, alarm.id)
        await db.commit()
        log = await db.scalar(
            select(NotificationLog).where(NotificationLog.alarm_id == alarm.id)
        )
    assert log is not None
    assert log.status in {"sent", "delivered"}


@pytest.mark.asyncio
async def test_escalation_resends_after_timeout(test_redis) -> None:
    from app.notifications.gateway_dispatcher import run_escalation_resend_once

    await run_escalation_resend_once(test_redis)
