"""Rule-based telemetry anomaly detection engine."""

from __future__ import annotations

import uuid
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from typing import Any

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.dependencies import CurrentUser
from app.devices.service import _get_device_for_user
from app.models.telemetry_anomaly import TelemetryAnomaly
from app.models.telemetry_reading import TelemetryReading
from app.mission.geofence_checker import GeofenceChecker
from app.mission.geofence_service import geofence_service
from app.telemetry.schemas import TelemetryAnomalyItem, TelemetryAnomalyResponse

ALLOWED_HOURS = frozenset({1, 24})

VOLTAGE_DROP_PCT = 15.0
VOLTAGE_DROP_CRITICAL_PCT = 25.0
OVERHEAT_TEMP_C = 55.0
OVERHEAT_CRITICAL_TEMP_C = 65.0
SIGNAL_RSSI_WEAK_DBM = -115.0
SIGNAL_RSSI_DROP_DBM = 20.0
PING_DELAY_MS = 5000.0
ALTITUDE_DEVIATION_M = 50.0
ALTITUDE_CRITICAL_M = 80.0
SPEED_DEVIATION_MS = 15.0
SPEED_CRITICAL_MS = 100.0


@dataclass(frozen=True)
class DetectedAnomaly:
    severity: str
    anomaly_type: str
    message: str
    metadata: dict[str, Any]


def _metric_float(metrics: dict[str, Any], *keys: str) -> float | None:
    for key in keys:
        if key in metrics and metrics[key] is not None:
            try:
                return float(metrics[key])
            except (TypeError, ValueError):
                continue
    return None


class TelemetryAnomalyDetector:
    """Evaluate incoming telemetry against threshold rules."""

    def evaluate(
        self,
        metrics: dict[str, Any],
        *,
        previous_metrics: dict[str, Any] | None = None,
    ) -> list[DetectedAnomaly]:
        anomalies: list[DetectedAnomaly] = []
        prev = previous_metrics or {}

        voltage = _metric_float(metrics, "voltage", "battery_voltage", "batt_voltage")
        prev_voltage = _metric_float(prev, "voltage", "battery_voltage", "batt_voltage")
        if voltage is not None and prev_voltage is not None and prev_voltage > 0:
            drop_pct = ((prev_voltage - voltage) / prev_voltage) * 100.0
            if drop_pct > VOLTAGE_DROP_PCT:
                severity = "critical" if drop_pct > VOLTAGE_DROP_CRITICAL_PCT else "warning"
                anomalies.append(
                    DetectedAnomaly(
                        severity=severity,
                        anomaly_type="voltage_drop",
                        message=f"Voltage dropped {drop_pct:.1f}% ({prev_voltage:.2f}V → {voltage:.2f}V)",
                        metadata={
                            "previous_voltage": prev_voltage,
                            "current_voltage": voltage,
                            "drop_percent": round(drop_pct, 2),
                        },
                    )
                )

        temp = _metric_float(metrics, "temperature", "temp", "battery_temp")
        if temp is not None and temp > OVERHEAT_TEMP_C:
            severity = "critical" if temp > OVERHEAT_CRITICAL_TEMP_C else "warning"
            anomalies.append(
                DetectedAnomaly(
                    severity=severity,
                    anomaly_type="battery_overheat",
                    message=f"Battery temperature {temp:.1f}°C exceeds {OVERHEAT_TEMP_C}°C threshold",
                    metadata={"temperature_c": temp, "threshold_c": OVERHEAT_TEMP_C},
                )
            )

        rssi = _metric_float(metrics, "rssi", "signal_rssi")
        prev_rssi = _metric_float(prev, "rssi", "signal_rssi")
        ping_delay = _metric_float(metrics, "ping_delay", "ping_delay_ms", "latency_ms")
        signal_triggered = False

        if rssi is not None and rssi <= SIGNAL_RSSI_WEAK_DBM:
            anomalies.append(
                DetectedAnomaly(
                    severity="critical",
                    anomaly_type="signal_loss",
                    message=f"Signal critically weak at {rssi:.1f} dBm",
                    metadata={"rssi_dbm": rssi, "threshold_dbm": SIGNAL_RSSI_WEAK_DBM},
                )
            )
            signal_triggered = True

        if (
            not signal_triggered
            and rssi is not None
            and prev_rssi is not None
            and (prev_rssi - rssi) > SIGNAL_RSSI_DROP_DBM
        ):
            drop = prev_rssi - rssi
            anomalies.append(
                DetectedAnomaly(
                    severity="warning",
                    anomaly_type="signal_loss",
                    message=f"Sudden signal loss: RSSI dropped {drop:.1f} dBm",
                    metadata={
                        "previous_rssi_dbm": prev_rssi,
                        "current_rssi_dbm": rssi,
                        "drop_dbm": round(drop, 2),
                    },
                )
            )
            signal_triggered = True

        if ping_delay is not None and ping_delay > PING_DELAY_MS:
            anomalies.append(
                DetectedAnomaly(
                    severity="warning" if ping_delay < PING_DELAY_MS * 2 else "critical",
                    anomaly_type="signal_loss",
                    message=f"Ping delay {ping_delay:.0f} ms exceeds {PING_DELAY_MS:.0f} ms",
                    metadata={"ping_delay_ms": ping_delay, "threshold_ms": PING_DELAY_MS},
                )
            )

        altitude = _metric_float(metrics, "altitude", "alt", "altitude_m")
        prev_altitude = _metric_float(prev, "altitude", "alt", "altitude_m")
        if altitude is not None and prev_altitude is not None:
            delta = abs(altitude - prev_altitude)
            if delta > ALTITUDE_DEVIATION_M:
                severity = "critical" if delta > ALTITUDE_CRITICAL_M else "warning"
                anomalies.append(
                    DetectedAnomaly(
                        severity=severity,
                        anomaly_type="altitude_deviation",
                        message=f"Altitude changed {delta:.1f} m ({prev_altitude:.1f} → {altitude:.1f} m)",
                        metadata={
                            "previous_altitude_m": prev_altitude,
                            "current_altitude_m": altitude,
                            "delta_m": round(delta, 2),
                        },
                    )
                )

        speed = _metric_float(metrics, "speed", "groundspeed", "ground_speed")
        prev_speed = _metric_float(prev, "speed", "groundspeed", "ground_speed")
        if speed is not None and speed > SPEED_CRITICAL_MS:
            anomalies.append(
                DetectedAnomaly(
                    severity="critical",
                    anomaly_type="speed_deviation",
                    message=f"Speed {speed:.1f} m/s exceeds safe limit",
                    metadata={"speed_ms": speed, "threshold_ms": SPEED_CRITICAL_MS},
                )
            )
        elif speed is not None and prev_speed is not None:
            delta = abs(speed - prev_speed)
            if delta > SPEED_DEVIATION_MS:
                anomalies.append(
                    DetectedAnomaly(
                        severity="warning",
                        anomaly_type="speed_deviation",
                        message=f"Sudden speed change {delta:.1f} m/s ({prev_speed:.1f} → {speed:.1f} m/s)",
                        metadata={
                            "previous_speed_ms": prev_speed,
                            "current_speed_ms": speed,
                            "delta_ms": round(delta, 2),
                        },
                    )
                )

        return anomalies


async def _fetch_previous_reading(
    db: AsyncSession,
    *,
    device_id: uuid.UUID,
    tenant_id: uuid.UUID,
    before: datetime,
) -> TelemetryReading | None:
    query = (
        select(TelemetryReading)
        .where(
            TelemetryReading.device_id == device_id,
            TelemetryReading.tenant_id == tenant_id,
            TelemetryReading.recorded_at < before,
        )
        .order_by(TelemetryReading.recorded_at.desc())
        .limit(1)
    )
    return await db.scalar(query)


def _geofence_severity(action_on_breach: str, breach_type: str) -> str:
    if action_on_breach in {"RTL", "LAND"}:
        return "critical"
    if breach_type == "altitude_violation":
        return "critical"
    return "warning"


async def _detect_geofence_anomalies(
    db: AsyncSession,
    *,
    tenant_id: uuid.UUID,
    metrics: dict[str, Any],
) -> list[DetectedAnomaly]:
    lat = _metric_float(metrics, "latitude", "lat")
    lon = _metric_float(metrics, "longitude", "lon")
    if lat is None or lon is None:
        return []

    altitude = _metric_float(metrics, "altitude", "alt", "altitude_m")
    zones = await geofence_service.fetch_snapshots_for_tenant(db, tenant_id)
    if not zones:
        return []

    checker = GeofenceChecker()
    breaches = checker.check_position(lat, lon, altitude, zones)
    anomalies: list[DetectedAnomaly] = []
    for breach in breaches:
        severity = _geofence_severity(breach.action_on_breach, breach.breach_type)
        anomalies.append(
            DetectedAnomaly(
                severity=severity,
                anomaly_type="geofence_breach",
                message=breach.message,
                metadata=breach.metadata,
            )
        )
    return anomalies


async def detect_and_persist_anomalies(
    db: AsyncSession,
    *,
    device_id: uuid.UUID,
    tenant_id: uuid.UUID,
    metrics: dict[str, Any],
    recorded_at: datetime,
    reading_id: uuid.UUID,
) -> list[TelemetryAnomaly]:
    previous = await _fetch_previous_reading(
        db,
        device_id=device_id,
        tenant_id=tenant_id,
        before=recorded_at,
    )
    previous_metrics = previous.metrics if previous else None

    detector = TelemetryAnomalyDetector()
    detected = detector.evaluate(metrics, previous_metrics=previous_metrics)
    detected.extend(
        await _detect_geofence_anomalies(
            db,
            tenant_id=tenant_id,
            metrics=metrics,
        )
    )
    if not detected:
        return []

    lat = _metric_float(metrics, "latitude", "lat")
    lon = _metric_float(metrics, "longitude", "lon")

    rows: list[TelemetryAnomaly] = []
    for item in detected:
        metadata = dict(item.metadata)
        if lat is not None and lon is not None:
            metadata.setdefault("lat", lat)
            metadata.setdefault("lon", lon)
        row = TelemetryAnomaly(
            device_id=device_id,
            tenant_id=tenant_id,
            reading_id=reading_id,
            severity=item.severity,
            anomaly_type=item.anomaly_type,
            message=item.message,
            metadata_=metadata,
            recorded_at=recorded_at,
        )
        db.add(row)
        rows.append(row)

    await db.flush()
    return rows


async def get_anomalies(
    db: AsyncSession,
    user: CurrentUser,
    *,
    device_id: uuid.UUID,
    hours: int = 24,
) -> TelemetryAnomalyResponse:
    if hours not in ALLOWED_HOURS:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="hours must be 1 or 24",
        )

    await _get_device_for_user(db, device_id, user)
    since = datetime.now(UTC) - timedelta(hours=hours)

    query = (
        select(TelemetryAnomaly)
        .where(
            TelemetryAnomaly.device_id == device_id,
            TelemetryAnomaly.recorded_at >= since,
        )
        .order_by(TelemetryAnomaly.recorded_at.desc())
        .limit(500)
    )
    if not user.is_super_admin:
        query = query.where(TelemetryAnomaly.tenant_id == user.tenant_id)

    rows = (await db.scalars(query)).all()
    items = [
        TelemetryAnomalyItem(
            id=row.id,
            device_id=row.device_id,
            severity=row.severity,
            anomaly_type=row.anomaly_type,
            message=row.message,
            metadata=row.metadata_ or {},
            recorded_at=row.recorded_at,
            detected_at=row.detected_at,
        )
        for row in rows
    ]

    return TelemetryAnomalyResponse(
        device_id=device_id,
        hours=hours,
        count=len(items),
        items=items,
    )
