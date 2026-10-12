"""Agriculture vertical HTTP API."""

from __future__ import annotations

import uuid

from fastapi import APIRouter, Query, Response

from app.agriculture import service as svc
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
    ValveCreateRequest,
    ValveOpenRequest,
    ValveResponse,
    ValveScheduleUpdate,
    YieldRecordRequest,
    YieldRecordResponse,
)
from app.auth.dependencies import RequireAuth
from app.deps import DbSession, RedisDep

router = APIRouter(prefix="/api/agriculture", tags=["agriculture"])


@router.get("/farms")
async def list_farms(user: RequireAuth, db: DbSession) -> list[FarmResponse]:
    return await svc.list_farms(db, user)


@router.post("/farms", status_code=201)
async def create_farm(user: RequireAuth, db: DbSession, payload: FarmCreateRequest) -> FarmResponse:
    return await svc.create_farm(db, user, payload)


@router.get("/farms/{farm_id}")
async def get_farm(user: RequireAuth, db: DbSession, farm_id: uuid.UUID) -> FarmResponse:
    return await svc.get_farm(db, user, farm_id)


@router.put("/farms/{farm_id}")
async def update_farm(
    user: RequireAuth, db: DbSession, farm_id: uuid.UUID, payload: FarmUpdateRequest
) -> FarmResponse:
    return await svc.update_farm(db, user, farm_id, payload)


@router.delete("/farms/{farm_id}", status_code=204, response_class=Response)
async def delete_farm(user: RequireAuth, db: DbSession, farm_id: uuid.UUID) -> Response:
    await svc.delete_farm(db, user, farm_id)
    return Response(status_code=204)


@router.get("/farms/{farm_id}/overview")
async def farm_overview(user: RequireAuth, db: DbSession, farm_id: uuid.UUID) -> FarmOverviewResponse:
    return await svc.farm_overview(db, user, farm_id)


@router.get("/farms/{farm_id}/plots")
async def list_plots(user: RequireAuth, db: DbSession, farm_id: uuid.UUID) -> list[PlotResponse]:
    return await svc.list_plots(db, user, farm_id)


@router.post("/farms/{farm_id}/plots", status_code=201)
async def create_plot(
    user: RequireAuth, db: DbSession, farm_id: uuid.UUID, payload: PlotCreateRequest
) -> PlotResponse:
    return await svc.create_plot(db, user, farm_id, payload)


@router.get("/plots/{plot_id}")
async def get_plot(user: RequireAuth, db: DbSession, plot_id: uuid.UUID) -> PlotResponse:
    return await svc.get_plot(db, user, plot_id)


@router.put("/plots/{plot_id}")
async def update_plot(
    user: RequireAuth, db: DbSession, plot_id: uuid.UUID, payload: PlotUpdateRequest
) -> PlotResponse:
    return await svc.update_plot(db, user, plot_id, payload)


@router.get("/plots/{plot_id}/heatmap")
async def plot_heatmap(user: RequireAuth, db: DbSession, plot_id: uuid.UUID) -> list[HeatmapPoint]:
    return await svc.plot_heatmap(db, user, plot_id)


@router.get("/farms/{farm_id}/sensors")
async def list_sensors(user: RequireAuth, db: DbSession, farm_id: uuid.UUID) -> list[SensorResponse]:
    return await svc.list_sensors(db, user, farm_id)


@router.post("/farms/{farm_id}/sensors", status_code=201)
async def commission_sensor(
    user: RequireAuth, db: DbSession, farm_id: uuid.UUID, payload: SensorCommissionRequest
) -> SensorResponse:
    return await svc.commission_sensor(db, user, farm_id, payload)


@router.get("/sensors/{sensor_id}/readings")
async def sensor_readings(
    user: RequireAuth,
    db: DbSession,
    sensor_id: uuid.UUID,
    aggregation: str = Query(default="hourly"),
    hours: int = Query(default=24, ge=1, le=720),
) -> list[ReadingPoint]:
    return await svc.sensor_readings(db, user, sensor_id, aggregation=aggregation, hours=hours)


@router.post("/sensors/{sensor_id}/calibrate")
async def calibrate_sensor(
    user: RequireAuth, db: DbSession, sensor_id: uuid.UUID, payload: SensorCalibrateRequest
) -> SensorResponse:
    return await svc.calibrate_sensor(db, user, sensor_id, payload)


@router.get("/sensors/{sensor_id}/battery-history")
async def sensor_battery_history(
    user: RequireAuth, db: DbSession, sensor_id: uuid.UUID
) -> list[dict[str, object]]:
    return await svc.sensor_battery_history(db, user, sensor_id)


@router.get("/gateways")
async def list_gateways(user: RequireAuth, db: DbSession) -> list[GatewayResponse]:
    return await svc.list_gateways(db, user)


@router.post("/gateways", status_code=201)
async def create_gateway(user: RequireAuth, db: DbSession, payload: GatewayCreateRequest) -> GatewayResponse:
    return await svc.create_gateway(db, user, payload)


@router.get("/gateways/{gateway_id}/stats")
async def gateway_stats(user: RequireAuth, db: DbSession, gateway_id: uuid.UUID) -> GatewayStatsResponse:
    return await svc.gateway_stats(db, user, gateway_id)


@router.get("/plots/{plot_id}/valves")
async def list_valves(user: RequireAuth, db: DbSession, plot_id: uuid.UUID) -> list[ValveResponse]:
    return await svc.list_valves_for_plot(db, user, plot_id)


@router.post("/plots/{plot_id}/valves", status_code=201)
async def create_valve(
    user: RequireAuth, db: DbSession, plot_id: uuid.UUID, payload: ValveCreateRequest
) -> ValveResponse:
    return await svc.create_valve(
        db, user, plot_id, payload.name, payload.flow_rate_lpm, payload.valve_type
    )


@router.post("/valves/{valve_id}/open")
async def open_valve(
    user: RequireAuth, db: DbSession, valve_id: uuid.UUID, payload: ValveOpenRequest
) -> ValveResponse:
    return await svc.open_valve(db, user, valve_id, payload.duration_minutes)


@router.post("/valves/{valve_id}/close")
async def close_valve(user: RequireAuth, db: DbSession, valve_id: uuid.UUID) -> ValveResponse:
    return await svc.close_valve(db, user, valve_id)


@router.get("/valves/{valve_id}/schedule")
async def get_schedule(user: RequireAuth, db: DbSession, valve_id: uuid.UUID) -> dict[str, object]:
    return await svc.get_valve_schedule(db, user, valve_id)


@router.put("/valves/{valve_id}/schedule")
async def set_schedule(
    user: RequireAuth, db: DbSession, valve_id: uuid.UUID, payload: ValveScheduleUpdate
) -> ValveResponse:
    return await svc.set_valve_schedule(db, user, valve_id, payload.schedule)


@router.post("/farms/{farm_id}/irrigation/auto-run")
async def auto_irrigation(
    user: RequireAuth, db: DbSession, redis: RedisDep, farm_id: uuid.UUID
) -> dict[str, object]:
    return await svc.auto_irrigation_run(db, redis, user, farm_id)


@router.get("/farms/{farm_id}/disease-alerts")
async def disease_alerts(
    user: RequireAuth, db: DbSession, farm_id: uuid.UUID
) -> list[DiseaseAlertResponse]:
    return await svc.list_disease_alerts(db, user, farm_id)


@router.post("/disease-alerts/{alert_id}/acknowledge")
async def acknowledge_alert(
    user: RequireAuth, db: DbSession, alert_id: uuid.UUID
) -> DiseaseAlertResponse:
    return await svc.acknowledge_alert(db, user, alert_id)


@router.post("/disease-alerts/{alert_id}/resolve")
async def resolve_alert(user: RequireAuth, db: DbSession, alert_id: uuid.UUID) -> DiseaseAlertResponse:
    return await svc.resolve_alert(db, user, alert_id)


@router.get("/farms/{farm_id}/disease-risk-forecast")
async def disease_forecast(user: RequireAuth, db: DbSession, farm_id: uuid.UUID) -> list[dict[str, object]]:
    return await svc.disease_forecast(db, user, farm_id)


@router.get("/farms/{farm_id}/calendar")
async def list_calendar(user: RequireAuth, db: DbSession, farm_id: uuid.UUID) -> list[CalendarEntryResponse]:
    return await svc.list_calendar(db, user, farm_id)


@router.post("/farms/{farm_id}/calendar", status_code=201)
async def add_calendar(
    user: RequireAuth, db: DbSession, farm_id: uuid.UUID, payload: CalendarEntryRequest
) -> CalendarEntryResponse:
    return await svc.add_calendar_entry(db, user, farm_id, payload)


@router.get("/farms/{farm_id}/next-tasks")
async def next_tasks(user: RequireAuth, db: DbSession, farm_id: uuid.UUID) -> list[str]:
    return await svc.next_tasks(db, user, farm_id)


@router.get("/farms/{farm_id}/yield-records")
async def yield_records(user: RequireAuth, db: DbSession, farm_id: uuid.UUID) -> list[YieldRecordResponse]:
    return await svc.list_yield_records(db, user, farm_id)


@router.post("/plots/{plot_id}/yield", status_code=201)
async def record_yield(
    user: RequireAuth, db: DbSession, plot_id: uuid.UUID, payload: YieldRecordRequest
) -> YieldRecordResponse:
    return await svc.record_yield(db, user, plot_id, payload)


@router.get("/farms/{farm_id}/yield-analytics")
async def yield_analytics(user: RequireAuth, db: DbSession, farm_id: uuid.UUID) -> dict[str, object]:
    return await svc.yield_analytics(db, user, farm_id)


@router.get("/farms/{farm_id}/analytics/water-usage")
async def water_analytics(user: RequireAuth, db: DbSession, farm_id: uuid.UUID) -> AnalyticsSeries:
    return await svc.water_usage_analytics(db, user, farm_id)


@router.get("/farms/{farm_id}/analytics/environmental")
async def env_analytics(
    user: RequireAuth, db: DbSession, farm_id: uuid.UUID
) -> dict[str, AnalyticsSeries]:
    return await svc.environmental_analytics(db, user, farm_id)


@router.get("/farms/{farm_id}/analytics/cost-vs-yield")
async def cost_yield(user: RequireAuth, db: DbSession, farm_id: uuid.UUID) -> dict[str, float]:
    return await svc.cost_vs_yield(db, user, farm_id)
