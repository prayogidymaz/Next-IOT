"""BMKG weather forecast cache (Indonesia)."""

from __future__ import annotations

import json
import logging
from datetime import UTC, datetime, timedelta
from typing import Protocol

import httpx

from app.types.redis_client import RedisClient

logger = logging.getLogger(__name__)

CACHE_KEY_PREFIX = "agri:bmkg:"
CACHE_TTL_SECONDS = 3 * 3600


class WeatherForecast(Protocol):
    def rain_next_hours(self, hours: int) -> bool: ...


class BmkgForecast:
    def __init__(self, payload: dict[str, object]) -> None:
        self._payload = payload

    def rain_next_hours(self, hours: int) -> bool:
        alerts = self._payload.get("rain_alerts")
        if isinstance(alerts, list):
            for entry in alerts:
                if isinstance(entry, dict):
                    within = entry.get("within_hours")
                    if isinstance(within, int | float) and within <= hours:
                        return bool(entry.get("rain", False))
        return bool(self._payload.get("rain_forecast_6h", False))


async def fetch_bmkg_forecast(lat: float, lng: float) -> dict[str, object]:
    """Best-effort BMKG open data; falls back to stub when unreachable."""
    url = "https://api.bmkg.go.id/publik/prakiraan-cuaca"
    try:
        async with httpx.AsyncClient(timeout=8.0) as client:
            resp = await client.get(url, params={"adm4": f"{lat:.4f},{lng:.4f}"})
            if resp.status_code == 200:
                data = resp.json()
                if isinstance(data, dict):
                    return {"source": "bmkg", "raw": data, "rain_forecast_6h": False}
    except (httpx.HTTPError, json.JSONDecodeError) as exc:
        logger.debug("BMKG fetch failed: %s", exc)
    return {
        "source": "stub",
        "rain_forecast_6h": False,
        "updated_at": datetime.now(tz=UTC).isoformat(),
    }


async def get_cached_forecast(redis: RedisClient, lat: float, lng: float) -> BmkgForecast:
    key = f"{CACHE_KEY_PREFIX}{lat:.3f}:{lng:.3f}"
    cached = await redis.get(key)
    if cached:
        try:
            payload = json.loads(cached)
            if isinstance(payload, dict):
                return BmkgForecast(payload)
        except json.JSONDecodeError:
            pass
    payload = await fetch_bmkg_forecast(lat, lng)
    await redis.set(key, json.dumps(payload), ex=CACHE_TTL_SECONDS)
    return BmkgForecast(payload)


def irrigation_window_ok(now: datetime) -> bool:
    """Morning or evening windows (local time assumed UTC+7 in scheduler)."""
    hour = (now.hour + 7) % 24
    return (5 <= hour < 7) or (17 <= hour < 19)


def cache_expired(updated_at: datetime | None) -> bool:
    if updated_at is None:
        return True
    return datetime.now(tz=UTC) - updated_at > timedelta(hours=3)
