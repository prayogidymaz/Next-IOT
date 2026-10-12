"""Agri WA dispatcher tests."""

from __future__ import annotations

import uuid
from unittest.mock import AsyncMock, patch

import pytest
from app.agriculture.notification_dispatcher import AgriNotificationDispatcher, _render
from app.notifications.providers.channel_base import ProviderResult


def test_template_render_disease() -> None:
    body = _render(
        "disease_alert_high.jinja2",
        {
            "farm_name": "Kebun A",
            "disease_name": "Karat",
            "factors": "- humidity: 90",
            "action": "Semprot",
            "link": "/ag",
        },
    )
    assert "Kebun A" in body
    assert "Karat" in body


@pytest.mark.asyncio
async def test_send_dedup_skips_second(test_redis) -> None:
    from app.agriculture.models import AgriDiseaseAlert, AgriFarm, AgriPlot
    from app.database import async_session
    from app.models.tenant import Tenant

    async with async_session() as db:
        tenant = Tenant(name="T", slug=f"agri-wa-{uuid.uuid4().hex[:8]}")
        db.add(tenant)
        await db.flush()
        farm = AgriFarm(tenant_id=tenant.id, name="F", crop_type="coffee", owner_whatsapp="628111")
        db.add(farm)
        await db.flush()
        plot = AgriPlot(farm_id=farm.id, name="P")
        db.add(plot)
        await db.flush()
        alert = AgriDiseaseAlert(
            plot_id=plot.id,
            disease_name="X",
            risk_level="high",
            factors={},
            action_recommended="A",
        )
        db.add(alert)
        await db.commit()
        await db.refresh(alert)
        dispatcher = AgriNotificationDispatcher(db, test_redis)
        with patch.object(
            dispatcher._provider,
            "send",
            AsyncMock(return_value=ProviderResult(success=True, delivered=True)),
        ):
            first = await dispatcher.send_disease_alert(alert.id)
            second = await dispatcher.send_disease_alert(alert.id)
        assert first is True
        assert second is False
