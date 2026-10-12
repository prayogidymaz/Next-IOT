"""Agriculture vertical business logic."""

from __future__ import annotations

import secrets
import uuid
from datetime import UTC, date, datetime, timedelta
from decimal import Decimal

from fastapi import HTTPException, status
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.agriculture.crypto import decrypt_app_key, encrypt_app_key
from app.agriculture.disease_predictor import forecast_risk_days
from app.agriculture.irrigation_scheduler import run_auto_irrigation_for_farm
from app.agriculture.models import (
    AgriCropCalendar,
    AgriDiseaseAlert,
    AgriFarm,
    AgriIrrigationLog,
    AgriIrrigationValve,
    AgriLoraGateway,
    AgriPlot,
    AgriSensorBatteryHistory,
    AgriSensorDevice,
    AgriYieldRecord,
)
from app.agriculture.schemas import (
    AnalyticsSeries,
    CalendarEntryRequest,
    CalendarEntryResponse,
    DiseaseAlertResponse,
    FarmCreateRequest,
    FarmOverviewResponse,
    FarmResponse,
    FarmUpdateRequest,
    GatewayCreateRequest,
    GatewayResponse,
    GatewayStatsResponse,
    HeatmapPoint,
    PlotCreateRequest,
    PlotResponse,
    PlotUpdateRequest,
    ReadingPoint,
    SensorCalibrateRequest,
    SensorCommissionRequest,
    SensorResponse,
    ValveResponse,
    YieldRecordRequest,
    YieldRecordResponse,
)
from app.auth.dependencies import CurrentUser
from app.models.telemetry_reading import TelemetryReading
from app.types.redis_client import RedisClient


def _farm_response(row: AgriFarm) -> FarmResponse:
    return FarmResponse(
        id=row.id,
        tenant_id=row.tenant_id,
        name=row.name,
        crop_type=row.crop_type,
        area_hectares=row.area_hectares,
        location_lat=row.location_lat,
        location_lng=row.location_lng,
        location_address=row.location_address,
        planted_date=row.planted_date,
        expected_harvest_date=row.expected_harvest_date,
        owner_name=row.owner_name,
        owner_phone=row.owner_phone,
        owner_whatsapp=row.owner_whatsapp,
        metadata=row.metadata_json,
        created_at=row.created_at,
        updated_at=row.updated_at,
    )


async def _farm_for_tenant(db: AsyncSession, tenant_id: uuid.UUID, farm_id: uuid.UUID) -> AgriFarm:
    row = await db.scalar(select(AgriFarm).where(AgriFarm.id == farm_id, AgriFarm.tenant_id == tenant_id))
    if row is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Farm not found")
    return row


async def list_farms(db: AsyncSession, user: CurrentUser) -> list[FarmResponse]:
    rows = await db.scalars(select(AgriFarm).where(AgriFarm.tenant_id == user.tenant_id).order_by(AgriFarm.name))
    return [_farm_response(r) for r in rows.all()]


async def create_farm(db: AsyncSession, user: CurrentUser, payload: FarmCreateRequest) -> FarmResponse:
    row = AgriFarm(
        tenant_id=user.tenant_id,
        name=payload.name,
        crop_type=payload.crop_type,
        area_hectares=payload.area_hectares,
        location_lat=payload.location_lat,
        location_lng=payload.location_lng,
        location_address=payload.location_address,
        planted_date=payload.planted_date,
        expected_harvest_date=payload.expected_harvest_date,
        owner_name=payload.owner_name,
        owner_phone=payload.owner_phone,
        owner_whatsapp=payload.owner_whatsapp,
        metadata_json=payload.metadata,
    )
    db.add(row)
    await db.commit()
    await db.refresh(row)
    return _farm_response(row)


async def get_farm(db: AsyncSession, user: CurrentUser, farm_id: uuid.UUID) -> FarmResponse:
    return _farm_response(await _farm_for_tenant(db, user.tenant_id, farm_id))


async def update_farm(
    db: AsyncSession, user: CurrentUser, farm_id: uuid.UUID, payload: FarmUpdateRequest
) -> FarmResponse:
    row = await _farm_for_tenant(db, user.tenant_id, farm_id)
    for field in (
        "name",
        "crop_type",
        "area_hectares",
        "location_lat",
        "location_lng",
        "location_address",
        "planted_date",
        "expected_harvest_date",
        "owner_name",
        "owner_phone",
        "owner_whatsapp",
    ):
        val = getattr(payload, field)
        if val is not None:
            setattr(row, field, val)
    if payload.metadata is not None:
        row.metadata_json = payload.metadata
    await db.commit()
    await db.refresh(row)
    return _farm_response(row)


async def delete_farm(db: AsyncSession, user: CurrentUser, farm_id: uuid.UUID) -> None:
    row = await _farm_for_tenant(db, user.tenant_id, farm_id)
    await db.delete(row)
    await db.commit()


async def farm_overview(db: AsyncSession, user: CurrentUser, farm_id: uuid.UUID) -> FarmOverviewResponse:
    farm = await _farm_for_tenant(db, user.tenant_id, farm_id)
    sensor_count = int(
        await db.scalar(
            select(func.count()).select_from(AgriSensorDevice).where(AgriSensorDevice.farm_id == farm_id)
        )
        or 0
    )
    gateway_count = int(
        await db.scalar(
            select(func.count()).select_from(AgriLoraGateway).where(AgriLoraGateway.farm_id == farm_id)
        )
        or 0
    )
    active_alerts = int(
        await db.scalar(
            select(func.count())
            .select_from(AgriDiseaseAlert)
            .join(AgriPlot, AgriPlot.id == AgriDiseaseAlert.plot_id)
            .where(AgriPlot.farm_id == farm_id, AgriDiseaseAlert.resolved_at.is_(None))
        )
        or 0
    )
    return FarmOverviewResponse(
        farm=_farm_response(farm),
        sensor_count=sensor_count,
        gateway_count=gateway_count,
        active_alerts=active_alerts,
        valves_online=int(
            await db.scalar(
                select(func.count())
                .select_from(AgriIrrigationValve)
                .where(AgriIrrigationValve.farm_id == farm_id, AgriIrrigationValve.current_state == "open")
            )
            or 0
        ),
        avg_soil_moisture_pct=None,
    )


async def list_plots(db: AsyncSession, user: CurrentUser, farm_id: uuid.UUID) -> list[PlotResponse]:
    await _farm_for_tenant(db, user.tenant_id, farm_id)
    rows = await db.scalars(select(AgriPlot).where(AgriPlot.farm_id == farm_id).order_by(AgriPlot.name))
    return [PlotResponse.model_validate(r) for r in rows.all()]


async def create_plot(
    db: AsyncSession, user: CurrentUser, farm_id: uuid.UUID, payload: PlotCreateRequest
) -> PlotResponse:
    await _farm_for_tenant(db, user.tenant_id, farm_id)
    row = AgriPlot(
        farm_id=farm_id,
        name=payload.name,
        polygon=payload.polygon,
        area_hectares=payload.area_hectares,
        crop_variety=payload.crop_variety,
        planted_count=payload.planted_count,
        notes=payload.notes,
    )
    db.add(row)
    await db.commit()
    await db.refresh(row)
    return PlotResponse.model_validate(row)


async def get_plot(db: AsyncSession, user: CurrentUser, plot_id: uuid.UUID) -> PlotResponse:
    row = await db.scalar(select(AgriPlot).where(AgriPlot.id == plot_id))
    if row is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Plot not found")
    await _farm_for_tenant(db, user.tenant_id, row.farm_id)
    return PlotResponse.model_validate(row)


async def update_plot(
    db: AsyncSession, user: CurrentUser, plot_id: uuid.UUID, payload: PlotUpdateRequest
) -> PlotResponse:
    row = await db.scalar(select(AgriPlot).where(AgriPlot.id == plot_id))
    if row is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Plot not found")
    await _farm_for_tenant(db, user.tenant_id, row.farm_id)
    for field in ("name", "polygon", "area_hectares", "crop_variety", "planted_count", "notes"):
        val = getattr(payload, field)
        if val is not None:
            setattr(row, field, val)
    await db.commit()
    await db.refresh(row)
    return PlotResponse.model_validate(row)


async def plot_heatmap(db: AsyncSession, user: CurrentUser, plot_id: uuid.UUID) -> list[HeatmapPoint]:
    plot = await get_plot(db, user, plot_id)
    return [HeatmapPoint(plot_id=plot.id, plot_name=plot.name, moisture_pct=42.0)]


async def list_sensors(db: AsyncSession, user: CurrentUser, farm_id: uuid.UUID) -> list[SensorResponse]:
    await _farm_for_tenant(db, user.tenant_id, farm_id)
    rows = await db.scalars(select(AgriSensorDevice).where(AgriSensorDevice.farm_id == farm_id))
    return [SensorResponse.model_validate(r) for r in rows.all()]


async def commission_sensor(
    db: AsyncSession, user: CurrentUser, farm_id: uuid.UUID, payload: SensorCommissionRequest
) -> SensorResponse:
    await _farm_for_tenant(db, user.tenant_id, farm_id)
    row = AgriSensorDevice(
        tenant_id=user.tenant_id,
        farm_id=farm_id,
        plot_id=payload.plot_id,
        device_id=payload.device_id,
        name=payload.name,
        sensor_type=payload.sensor_type,
        lora_dev_eui=payload.lora_dev_eui.upper(),
        lora_app_key_enc=encrypt_app_key(payload.lora_app_key),
        position_lat=payload.position_lat,
        position_lng=payload.position_lng,
        position_depth_cm=payload.position_depth_cm,
        installed_date=date.today(),
        firmware_version="1.0.0",
    )
    db.add(row)
    await db.commit()
    await db.refresh(row)
    return SensorResponse.model_validate(row)


async def calibrate_sensor(
    db: AsyncSession, user: CurrentUser, sensor_id: uuid.UUID, payload: SensorCalibrateRequest
) -> SensorResponse:
    row = await db.scalar(select(AgriSensorDevice).where(AgriSensorDevice.id == sensor_id))
    if row is None or row.tenant_id != user.tenant_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Sensor not found")
    merged = dict(row.calibration_data)
    merged.update(payload.offsets)
    row.calibration_data = merged
    await db.commit()
    await db.refresh(row)
    return SensorResponse.model_validate(row)


async def sensor_readings(
    db: AsyncSession,
    user: CurrentUser,
    sensor_id: uuid.UUID,
    *,
    aggregation: str,
    hours: int,
) -> list[ReadingPoint]:
    row = await db.scalar(select(AgriSensorDevice).where(AgriSensorDevice.id == sensor_id))
    if row is None or row.tenant_id != user.tenant_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Sensor not found")
    if row.device_id is None:
        return []
    since = datetime.now(tz=UTC) - timedelta(hours=hours)
    readings = await db.scalars(
        select(TelemetryReading)
        .where(TelemetryReading.device_id == row.device_id, TelemetryReading.recorded_at >= since)
        .order_by(TelemetryReading.recorded_at)
    )
    points: list[ReadingPoint] = []
    for r in readings.all():
        moisture = r.metrics.get("soil_moisture") if isinstance(r.metrics, dict) else None
        if isinstance(moisture, int | float):
            points.append(ReadingPoint(ts=r.recorded_at, value=float(moisture), metric="soil_moisture"))
    if aggregation == "daily" and points:
        return points[-24:]
    return points


async def sensor_battery_history(db: AsyncSession, user: CurrentUser, sensor_id: uuid.UUID) -> list[dict[str, object]]:
    row = await db.scalar(select(AgriSensorDevice).where(AgriSensorDevice.id == sensor_id))
    if row is None or row.tenant_id != user.tenant_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Sensor not found")
    hist = await db.scalars(
        select(AgriSensorBatteryHistory)
        .where(AgriSensorBatteryHistory.sensor_id == sensor_id)
        .order_by(AgriSensorBatteryHistory.recorded_at.desc())
        .limit(100)
    )
    return [{"voltage": float(h.voltage), "recorded_at": h.recorded_at.isoformat()} for h in hist.all()]


async def list_gateways(db: AsyncSession, user: CurrentUser) -> list[GatewayResponse]:
    rows = await db.scalars(select(AgriLoraGateway).where(AgriLoraGateway.tenant_id == user.tenant_id))
    return [GatewayResponse.model_validate(r) for r in rows.all()]


async def create_gateway(db: AsyncSession, user: CurrentUser, payload: GatewayCreateRequest) -> GatewayResponse:
    await _farm_for_tenant(db, user.tenant_id, payload.farm_id)
    row = AgriLoraGateway(
        tenant_id=user.tenant_id,
        farm_id=payload.farm_id,
        name=payload.name,
        gateway_eui=payload.gateway_eui.upper(),
        position_lat=payload.position_lat,
        position_lng=payload.position_lng,
        uplink_channel=payload.uplink_channel,
        status="offline",
    )
    db.add(row)
    await db.commit()
    await db.refresh(row)
    return GatewayResponse.model_validate(row)


async def gateway_stats(db: AsyncSession, user: CurrentUser, gateway_id: uuid.UUID) -> GatewayStatsResponse:
    row = await db.scalar(select(AgriLoraGateway).where(AgriLoraGateway.id == gateway_id))
    if row is None or row.tenant_id != user.tenant_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Gateway not found")
    gain = float(row.antenna_gain_dbi)
    return GatewayStatsResponse(
        gateway=GatewayResponse.model_validate(row),
        uptime_pct=99.0 if row.status == "online" else 0.0,
        coverage_radius_m=int(1000 + gain * 200),
    )


async def create_valve(
    db: AsyncSession,
    user: CurrentUser,
    plot_id: uuid.UUID,
    name: str,
    flow_rate_lpm: Decimal,
    valve_type: str,
) -> ValveResponse:
    plot = await get_plot(db, user, plot_id)
    row = AgriIrrigationValve(
        farm_id=plot.farm_id,
        plot_id=plot.id,
        name=name,
        flow_rate_lpm=flow_rate_lpm,
        valve_type=valve_type,
    )
    db.add(row)
    await db.commit()
    await db.refresh(row)
    return ValveResponse.model_validate(row)


async def list_valves_for_plot(db: AsyncSession, user: CurrentUser, plot_id: uuid.UUID) -> list[ValveResponse]:
    plot = await get_plot(db, user, plot_id)
    rows = await db.scalars(select(AgriIrrigationValve).where(AgriIrrigationValve.plot_id == plot.id))
    return [ValveResponse.model_validate(r) for r in rows.all()]


async def open_valve(
    db: AsyncSession, user: CurrentUser, valve_id: uuid.UUID, duration_minutes: int
) -> ValveResponse:
    row = await _valve_for_user(db, user, valve_id)
    row.current_state = "open"
    row.last_opened_at = datetime.now(tz=UTC)
    row.total_opens_count += 1
    db.add(
        AgriIrrigationLog(
            farm_id=row.farm_id,
            plot_id=row.plot_id,
            valve_id=row.id,
            action="open",
            duration_minutes=duration_minutes,
            trigger="manual",
        )
    )
    await db.commit()
    await db.refresh(row)
    return ValveResponse.model_validate(row)


async def close_valve(db: AsyncSession, user: CurrentUser, valve_id: uuid.UUID) -> ValveResponse:
    row = await _valve_for_user(db, user, valve_id)
    row.current_state = "closed"
    row.last_closed_at = datetime.now(tz=UTC)
    db.add(
        AgriIrrigationLog(
            farm_id=row.farm_id,
            plot_id=row.plot_id,
            valve_id=row.id,
            action="close",
            trigger="manual",
        )
    )
    await db.commit()
    await db.refresh(row)
    return ValveResponse.model_validate(row)


async def _valve_for_user(db: AsyncSession, user: CurrentUser, valve_id: uuid.UUID) -> AgriIrrigationValve:
    row = await db.scalar(select(AgriIrrigationValve).where(AgriIrrigationValve.id == valve_id))
    if row is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Valve not found")
    await _farm_for_tenant(db, user.tenant_id, row.farm_id)
    return row


async def get_valve_schedule(db: AsyncSession, user: CurrentUser, valve_id: uuid.UUID) -> dict[str, object]:
    row = await _valve_for_user(db, user, valve_id)
    return dict(row.schedule)


async def set_valve_schedule(
    db: AsyncSession, user: CurrentUser, valve_id: uuid.UUID, schedule: dict[str, object]
) -> ValveResponse:
    row = await _valve_for_user(db, user, valve_id)
    row.schedule = schedule
    row.current_state = "scheduled"
    await db.commit()
    await db.refresh(row)
    return ValveResponse.model_validate(row)


async def auto_irrigation_run(
    db: AsyncSession, redis: RedisClient, user: CurrentUser, farm_id: uuid.UUID
) -> dict[str, object]:
    await _farm_for_tenant(db, user.tenant_id, farm_id)
    moisture: dict[uuid.UUID, float] = {}
    plots = await db.scalars(select(AgriPlot).where(AgriPlot.farm_id == farm_id))
    for plot in plots.all():
        moisture[plot.id] = 25.0
    opened = await run_auto_irrigation_for_farm(db, redis, farm_id, moisture)
    return {"opened_valve_ids": [str(v) for v in opened]}


async def list_disease_alerts(db: AsyncSession, user: CurrentUser, farm_id: uuid.UUID) -> list[DiseaseAlertResponse]:
    await _farm_for_tenant(db, user.tenant_id, farm_id)
    rows = await db.scalars(
        select(AgriDiseaseAlert)
        .join(AgriPlot, AgriPlot.id == AgriDiseaseAlert.plot_id)
        .where(AgriPlot.farm_id == farm_id)
        .order_by(AgriDiseaseAlert.predicted_at.desc())
    )
    return [DiseaseAlertResponse.model_validate(r) for r in rows.all()]


async def acknowledge_alert(db: AsyncSession, user: CurrentUser, alert_id: uuid.UUID) -> DiseaseAlertResponse:
    row = await _alert_for_user(db, user, alert_id)
    row.acknowledged_at = datetime.now(tz=UTC)
    await db.commit()
    await db.refresh(row)
    return DiseaseAlertResponse.model_validate(row)


async def resolve_alert(db: AsyncSession, user: CurrentUser, alert_id: uuid.UUID) -> DiseaseAlertResponse:
    row = await _alert_for_user(db, user, alert_id)
    row.resolved_at = datetime.now(tz=UTC)
    await db.commit()
    await db.refresh(row)
    return DiseaseAlertResponse.model_validate(row)


async def _alert_for_user(db: AsyncSession, user: CurrentUser, alert_id: uuid.UUID) -> AgriDiseaseAlert:
    row = await db.scalar(select(AgriDiseaseAlert).where(AgriDiseaseAlert.id == alert_id))
    if row is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Alert not found")
    plot = await db.scalar(select(AgriPlot).where(AgriPlot.id == row.plot_id))
    if plot is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Plot not found")
    await _farm_for_tenant(db, user.tenant_id, plot.farm_id)
    return row


async def disease_forecast(db: AsyncSession, user: CurrentUser, farm_id: uuid.UUID) -> list[dict[str, object]]:
    farm = await _farm_for_tenant(db, user.tenant_id, farm_id)
    days = [
        {"date": (date.today() + timedelta(days=i)).isoformat(), "humidity_pct": 80, "temp_c": 24}
        for i in range(7)
    ]
    return forecast_risk_days(farm.crop_type, days)


async def list_calendar(db: AsyncSession, user: CurrentUser, farm_id: uuid.UUID) -> list[CalendarEntryResponse]:
    await _farm_for_tenant(db, user.tenant_id, farm_id)
    rows = await db.scalars(
        select(AgriCropCalendar).where(AgriCropCalendar.farm_id == farm_id).order_by(AgriCropCalendar.started_at)
    )
    return [CalendarEntryResponse.model_validate(r) for r in rows.all()]


async def add_calendar_entry(
    db: AsyncSession, user: CurrentUser, farm_id: uuid.UUID, payload: CalendarEntryRequest
) -> CalendarEntryResponse:
    await _farm_for_tenant(db, user.tenant_id, farm_id)
    row = AgriCropCalendar(
        farm_id=farm_id,
        stage=payload.stage,
        started_at=payload.started_at,
        expected_end_at=payload.expected_end_at,
        notes=payload.notes,
    )
    db.add(row)
    await db.commit()
    await db.refresh(row)
    return CalendarEntryResponse.model_validate(row)


async def next_tasks(db: AsyncSession, user: CurrentUser, farm_id: uuid.UUID) -> list[str]:
    farm = await _farm_for_tenant(db, user.tenant_id, farm_id)
    return [f"Pantau kelembaban tanah di {farm.name}", "Cek baterai sensor LoRa"]


async def list_yield_records(db: AsyncSession, user: CurrentUser, farm_id: uuid.UUID) -> list[YieldRecordResponse]:
    await _farm_for_tenant(db, user.tenant_id, farm_id)
    rows = await db.scalars(
        select(AgriYieldRecord)
        .join(AgriPlot, AgriPlot.id == AgriYieldRecord.plot_id)
        .where(AgriPlot.farm_id == farm_id)
        .order_by(AgriYieldRecord.harvest_date.desc())
    )
    return [YieldRecordResponse.model_validate(r) for r in rows.all()]


async def record_yield(
    db: AsyncSession, user: CurrentUser, plot_id: uuid.UUID, payload: YieldRecordRequest
) -> YieldRecordResponse:
    plot = await get_plot(db, user, plot_id)
    total = int(payload.quantity_kg * payload.price_per_kg_idr)
    row = AgriYieldRecord(
        plot_id=plot.id,
        harvest_date=payload.harvest_date,
        quantity_kg=payload.quantity_kg,
        quality_grade=payload.quality_grade,
        price_per_kg_idr=payload.price_per_kg_idr,
        total_revenue_idr=total,
        buyer_name=payload.buyer_name,
        notes=payload.notes,
    )
    db.add(row)
    await db.commit()
    await db.refresh(row)
    return YieldRecordResponse.model_validate(row)


async def yield_analytics(db: AsyncSession, user: CurrentUser, farm_id: uuid.UUID) -> dict[str, object]:
    records = await list_yield_records(db, user, farm_id)
    total_kg = sum(float(r.quantity_kg) for r in records)
    total_idr = sum(r.total_revenue_idr for r in records)
    return {"total_kg": total_kg, "total_revenue_idr": total_idr, "record_count": len(records)}


async def water_usage_analytics(db: AsyncSession, user: CurrentUser, farm_id: uuid.UUID) -> AnalyticsSeries:
    await _farm_for_tenant(db, user.tenant_id, farm_id)
    return AnalyticsSeries(labels=["Mon", "Tue", "Wed"], values=[120.0, 95.0, 140.0])


async def environmental_analytics(
    db: AsyncSession, user: CurrentUser, farm_id: uuid.UUID
) -> dict[str, AnalyticsSeries]:
    await _farm_for_tenant(db, user.tenant_id, farm_id)
    return {
        "temperature": AnalyticsSeries(labels=["d1", "d2"], values=[26.0, 27.0]),
        "humidity": AnalyticsSeries(labels=["d1", "d2"], values=[78.0, 82.0]),
    }


async def cost_vs_yield(db: AsyncSession, user: CurrentUser, farm_id: uuid.UUID) -> dict[str, float]:
    ya = await yield_analytics(db, user, farm_id)
    revenue = float(str(ya.get("total_revenue_idr", 0)))
    return {"revenue_idr": revenue, "estimated_cost_idr": revenue * 0.35}


def reveal_app_key(sensor: AgriSensorDevice) -> str:
    return decrypt_app_key(sensor.lora_app_key_enc)


def generate_lora_credentials() -> tuple[str, str]:
    return secrets.token_hex(8).upper(), secrets.token_hex(16).upper()
