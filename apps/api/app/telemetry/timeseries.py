"""Time-series bucketing and per-metric statistics for telemetry analytics."""

from __future__ import annotations

import uuid
from datetime import UTC, datetime, timedelta
from typing import TypedDict

from pydantic import JsonValue
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.dependencies import CurrentUser
from app.devices.service import _get_device_for_user
from app.models.telemetry_reading import TelemetryReading
from app.types.json_types import json_value_to_float


class MetricStatsDict(TypedDict):
    avg: float | None
    min: float | None
    max: float | None
    latest: float | None


class BucketPointDict(TypedDict):
    bucket_start: datetime
    avg: float
    min: float
    max: float
    count: int


class AggregatedSeriesItem(TypedDict):
    metric: str
    stats: MetricStatsDict
    points: list[BucketPointDict]

ALLOWED_INTERVALS = {
    "1m": timedelta(minutes=1),
    "5m": timedelta(minutes=5),
    "1h": timedelta(hours=1),
    "1d": timedelta(days=1),
}

MAX_ANALYTICS_READINGS = 20_000


def parse_interval(interval: str) -> timedelta:
    key = interval.strip().lower()
    if key not in ALLOWED_INTERVALS:
        raise ValueError(f"interval must be one of: {', '.join(sorted(ALLOWED_INTERVALS))}")
    return ALLOWED_INTERVALS[key]


def resolve_time_window(
    *,
    start_time: datetime | None,
    end_time: datetime | None,
    hours: int | None,
) -> tuple[datetime, datetime]:
    end = end_time or datetime.now(UTC)
    if end.tzinfo is None:
        end = end.replace(tzinfo=UTC)
    if start_time is not None:
        start = start_time if start_time.tzinfo else start_time.replace(tzinfo=UTC)
        return start, end
    lookback = hours if hours is not None else 24
    return end - timedelta(hours=lookback), end


def _metric_value(metrics: dict[str, JsonValue], metric: str) -> float | None:
    return json_value_to_float(metrics.get(metric))


def _floor_bucket(ts: datetime, bucket: timedelta) -> datetime:
    epoch = datetime(1970, 1, 1, tzinfo=UTC)
    seconds = (ts - epoch).total_seconds()
    step = bucket.total_seconds()
    floored = int(seconds // step) * step
    return epoch + timedelta(seconds=floored)


def aggregate_timeseries(
    readings: list[TelemetryReading],
    *,
    metrics: list[str],
    interval: timedelta,
) -> list[AggregatedSeriesItem]:
    """Return list of {metric, stats, points} for each requested metric."""
    if not metrics:
        discovered: set[str] = set()
        for reading in readings[:50]:
            for key, value in (reading.metrics or {}).items():
                if isinstance(value, int | float) or (
                    isinstance(value, str) and value.replace(".", "", 1).isdigit()
                ):
                    discovered.add(key)
        metrics = sorted(discovered)[:8]

    series_output: list[AggregatedSeriesItem] = []

    for metric in metrics:
        values_by_time: list[tuple[datetime, float]] = []
        for reading in readings:
            value = _metric_value(reading.metrics or {}, metric)
            if value is not None:
                values_by_time.append((reading.recorded_at, value))

        if not values_by_time:
            series_output.append(
                {
                    "metric": metric,
                    "stats": {"avg": None, "min": None, "max": None, "latest": None},
                    "points": [],
                }
            )
            continue

        raw_values = [v for _, v in values_by_time]
        latest = raw_values[-1]
        stats: MetricStatsDict = {
            "avg": round(sum(raw_values) / len(raw_values), 4),
            "min": round(min(raw_values), 4),
            "max": round(max(raw_values), 4),
            "latest": round(latest, 4),
        }

        buckets: dict[datetime, list[float]] = {}
        for ts, val in values_by_time:
            bucket_start = _floor_bucket(ts if ts.tzinfo else ts.replace(tzinfo=UTC), interval)
            buckets.setdefault(bucket_start, []).append(val)

        points: list[BucketPointDict] = []
        for bucket_start in sorted(buckets):
            vals = buckets[bucket_start]
            point: BucketPointDict = {
                "bucket_start": bucket_start,
                "avg": round(sum(vals) / len(vals), 4),
                "min": round(min(vals), 4),
                "max": round(max(vals), 4),
                "count": len(vals),
            }
            points.append(point)

        item: AggregatedSeriesItem = {"metric": metric, "stats": stats, "points": points}
        series_output.append(item)

    return series_output


async def fetch_readings_window(
    db: AsyncSession,
    user: CurrentUser,
    *,
    device_id: uuid.UUID,
    start: datetime,
    end: datetime,
) -> list[TelemetryReading]:
    await _get_device_for_user(db, device_id, user)
    query = (
        select(TelemetryReading)
        .where(
            TelemetryReading.device_id == device_id,
            TelemetryReading.recorded_at >= start,
            TelemetryReading.recorded_at <= end,
        )
        .order_by(TelemetryReading.recorded_at.asc())
        .limit(MAX_ANALYTICS_READINGS)
    )
    if not user.is_super_admin:
        query = query.where(TelemetryReading.tenant_id == user.tenant_id)
    return list(await db.scalars(query))
