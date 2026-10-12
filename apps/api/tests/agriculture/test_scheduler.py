"""Irrigation scheduler unit tests."""

from __future__ import annotations

from datetime import UTC, datetime
from decimal import Decimal

from app.agriculture.bmkg_weather import BmkgForecast, irrigation_window_ok
from app.agriculture.irrigation_scheduler import minutes_for_plot


def test_minutes_for_plot_bounds() -> None:
    assert minutes_for_plot(Decimal("1"), Decimal("10")) >= 5


def test_irrigation_window_morning() -> None:
    morning = datetime(2026, 1, 1, 23, 30, tzinfo=UTC)  # 06:30 WIB
    assert irrigation_window_ok(morning) is True


def test_bmkg_rain_stub() -> None:
    fc = BmkgForecast({"rain_forecast_6h": True, "rain_alerts": [{"within_hours": 3, "rain": True}]})
    assert fc.rain_next_hours(6) is True
