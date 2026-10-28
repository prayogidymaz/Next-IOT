"""ML analytics service layer (DB + mesh events)."""

from __future__ import annotations

import uuid
from datetime import UTC, datetime, timedelta
from decimal import Decimal

import pandas as pd
from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.analytics.ml.anomaly_detector import AnomalyDetector
from app.analytics.ml.cost_optimizer import CostOptimizer
from app.analytics.ml.models import AnomalyEventRow, OptimizationReportRow, YieldForecastRow
from app.analytics.ml.schemas import OptimizationReport, YieldForecast
from app.analytics.ml.yield_predictor import YieldPredictor
from app.mesh.event_bus import MeshDomain
from app.mesh.publisher import get_mesh_publisher
from app.models.device import Device
from app.models.telemetry_reading import TelemetryReading
from app.types.json_types import JsonObject


async def forecast_yield(
    db: AsyncSession,
    tenant_id: uuid.UUID,
    plot_id: uuid.UUID,
    horizon_days: int,
) -> YieldForecast:
    predictor = YieldPredictor()
    historical = await _load_yield_training_frame(db, tenant_id, plot_id)
    if not historical.empty:
        predictor.fit(historical)
    forecast = predictor.predict(plot_id, horizon_days)
    row = YieldForecastRow(
        tenant_id=tenant_id,
        plot_id=plot_id,
        forecast_date=forecast.forecast_date,
        estimated_kg=Decimal(str(forecast.estimated_kg)),
        ci_low=Decimal(str(forecast.confidence_interval[0])),
        ci_high=Decimal(str(forecast.confidence_interval[1])),
        model_version=forecast.model_version,
    )
    db.add(row)
    await db.flush()
    return forecast


async def list_anomalies(
    db: AsyncSession,
    tenant_id: uuid.UUID,
    device_id: uuid.UUID | None,
    since: datetime | None,
    severity: str | None,
) -> list[AnomalyEventRow]:
    query = select(AnomalyEventRow).where(AnomalyEventRow.tenant_id == tenant_id)
    if device_id is not None:
        query = query.where(AnomalyEventRow.device_id == device_id)
    if since is not None:
        query = query.where(AnomalyEventRow.detected_at >= since)
    if severity is not None:
        query = query.where(AnomalyEventRow.severity == severity)
    query = query.order_by(AnomalyEventRow.detected_at.desc()).limit(200)
    result = await db.scalars(query)
    return list(result.all())


async def acknowledge_anomaly(db: AsyncSession, tenant_id: uuid.UUID, anomaly_id: uuid.UUID) -> AnomalyEventRow:
    row = await db.get(AnomalyEventRow, anomaly_id)
    if row is None or row.tenant_id != tenant_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Anomaly not found")
    row.acknowledged = True
    await db.flush()
    return row


async def optimization_report(
    db: AsyncSession,
    tenant_id: uuid.UUID,
    period_days: int,
) -> OptimizationReport:
    optimizer = CostOptimizer()
    report = optimizer.recommend(tenant_id, period_days)
    end = datetime.now(tz=UTC)
    start = end - timedelta(days=period_days)
    db.add(
        OptimizationReportRow(
            tenant_id=tenant_id,
            period_start=start,
            period_end=end,
            recommendations_json=report.recommendations,
            total_saving_idr=report.total_potential_saving_idr,
        )
    )
    await db.flush()
    return report


async def run_ml_anomaly_tick(db: AsyncSession) -> int:
    """Scan recent telemetry per device; persist anomalies and emit mesh events."""
    detector = AnomalyDetector(z_sigma=3.0)
    since = datetime.now(tz=UTC) - timedelta(hours=6)
    devices = list((await db.scalars(select(Device).limit(50))).all())
    publisher = get_mesh_publisher()
    inserted = 0
    for device in devices:
        readings = list(
            (
                await db.scalars(
                    select(TelemetryReading)
                    .where(
                        TelemetryReading.device_id == device.id,
                        TelemetryReading.recorded_at >= since,
                    )
                    .order_by(TelemetryReading.recorded_at.asc())
                    .limit(120)
                )
            ).all()
        )
        if len(readings) < 8:
            continue
        values: list[float] = []
        metric_name = "value"
        timestamps: list[datetime] = []
        for reading in readings:
            metrics = reading.metrics
            if not isinstance(metrics, dict):
                continue
            picked_key = next(iter(metrics.keys()), None)
            if picked_key is None:
                continue
            raw = metrics[picked_key]
            if isinstance(raw, (int, float)):
                values.append(float(raw))
                metric_name = str(picked_key)
                timestamps.append(reading.recorded_at)
        if len(values) < 8:
            continue
        frame = pd.DataFrame(
            {
                "value": values,
                "metric": [metric_name] * len(values),
                "recorded_at": timestamps,
            }
        )
        found = detector.detect(frame, device.id)
        for item in found:
            row = AnomalyEventRow(
                tenant_id=device.tenant_id,
                device_id=device.id,
                detected_at=item.detected_at,
                metric=item.metric,
                value=Decimal(str(item.value)),
                expected_min=Decimal(str(item.expected_range[0])),
                expected_max=Decimal(str(item.expected_range[1])),
                severity=item.severity,
            )
            db.add(row)
            inserted += 1
            if publisher is not None:
                payload: JsonObject = {
                    "event": "anomaly.detected",
                    "metric": item.metric,
                    "value": item.value,
                    "severity": item.severity,
                    "expected_min": item.expected_range[0],
                    "expected_max": item.expected_range[1],
                }
                await publisher.publish_event(
                    db,
                    tenant_id=device.tenant_id,
                    domain=MeshDomain.SENSOR,
                    event_type="anomaly_detected",
                    device_id=device.id,
                    payload=payload,
                )
    return inserted


async def _load_yield_training_frame(
    db: AsyncSession,
    tenant_id: uuid.UUID,
    plot_id: uuid.UUID,
) -> pd.DataFrame:
    _ = tenant_id, plot_id
    return pd.DataFrame()
