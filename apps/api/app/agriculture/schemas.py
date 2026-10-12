"""Pydantic schemas for agriculture API."""

from __future__ import annotations

import uuid
from datetime import date, datetime
from decimal import Decimal

from pydantic import BaseModel, Field


class FarmCreateRequest(BaseModel):
    name: str = Field(min_length=1, max_length=255)
    crop_type: str = Field(default="other")
    area_hectares: Decimal = Field(default=Decimal("0"))
    location_lat: Decimal | None = None
    location_lng: Decimal | None = None
    location_address: str = ""
    planted_date: date | None = None
    expected_harvest_date: date | None = None
    owner_name: str = ""
    owner_phone: str = ""
    owner_whatsapp: str = ""
    metadata: dict[str, object] = Field(default_factory=dict)


class FarmUpdateRequest(BaseModel):
    name: str | None = None
    crop_type: str | None = None
    area_hectares: Decimal | None = None
    location_lat: Decimal | None = None
    location_lng: Decimal | None = None
    location_address: str | None = None
    planted_date: date | None = None
    expected_harvest_date: date | None = None
    owner_name: str | None = None
    owner_phone: str | None = None
    owner_whatsapp: str | None = None
    metadata: dict[str, object] | None = None


class FarmResponse(BaseModel):
    id: uuid.UUID
    tenant_id: uuid.UUID
    name: str
    crop_type: str
    area_hectares: Decimal
    location_lat: Decimal | None
    location_lng: Decimal | None
    location_address: str
    planted_date: date | None
    expected_harvest_date: date | None
    owner_name: str
    owner_phone: str
    owner_whatsapp: str
    metadata: dict[str, object]
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class FarmOverviewResponse(BaseModel):
    farm: FarmResponse
    sensor_count: int
    gateway_count: int
    active_alerts: int
    valves_online: int
    avg_soil_moisture_pct: float | None


class PlotCreateRequest(BaseModel):
    name: str
    polygon: dict[str, object] = Field(default_factory=dict)
    area_hectares: Decimal = Decimal("0")
    crop_variety: str = ""
    planted_count: int = 0
    notes: str = ""


class PlotUpdateRequest(BaseModel):
    name: str | None = None
    polygon: dict[str, object] | None = None
    area_hectares: Decimal | None = None
    crop_variety: str | None = None
    planted_count: int | None = None
    notes: str | None = None


class PlotResponse(BaseModel):
    id: uuid.UUID
    farm_id: uuid.UUID
    name: str
    polygon: dict[str, object]
    area_hectares: Decimal
    crop_variety: str
    planted_count: int
    notes: str

    model_config = {"from_attributes": True}


class HeatmapPoint(BaseModel):
    plot_id: uuid.UUID
    plot_name: str
    moisture_pct: float | None


class SensorCommissionRequest(BaseModel):
    name: str
    sensor_type: str
    lora_dev_eui: str = Field(min_length=8, max_length=16)
    lora_app_key: str = Field(min_length=8, max_length=32)
    plot_id: uuid.UUID | None = None
    device_id: uuid.UUID | None = None
    position_lat: Decimal | None = None
    position_lng: Decimal | None = None
    position_depth_cm: int | None = None


class SensorResponse(BaseModel):
    id: uuid.UUID
    farm_id: uuid.UUID
    plot_id: uuid.UUID | None
    device_id: uuid.UUID | None
    name: str
    sensor_type: str
    lora_dev_eui: str
    position_lat: Decimal | None
    position_lng: Decimal | None
    last_battery_voltage: Decimal | None
    last_rssi: int | None
    firmware_version: str

    model_config = {"from_attributes": True}


class SensorCalibrateRequest(BaseModel):
    offsets: dict[str, float] = Field(default_factory=dict)


class ReadingPoint(BaseModel):
    ts: datetime
    value: float
    metric: str


class GatewayCreateRequest(BaseModel):
    farm_id: uuid.UUID
    name: str
    gateway_eui: str
    position_lat: Decimal | None = None
    position_lng: Decimal | None = None
    uplink_channel: str = "ethernet"


class GatewayResponse(BaseModel):
    id: uuid.UUID
    farm_id: uuid.UUID
    name: str
    gateway_eui: str
    status: str
    packets_rx_total: int
    packets_tx_total: int
    last_seen_at: datetime | None

    model_config = {"from_attributes": True}


class GatewayStatsResponse(BaseModel):
    gateway: GatewayResponse
    uptime_pct: float
    coverage_radius_m: int


class ValveResponse(BaseModel):
    id: uuid.UUID
    farm_id: uuid.UUID
    plot_id: uuid.UUID
    name: str
    current_state: str
    flow_rate_lpm: Decimal
    schedule: dict[str, object]

    model_config = {"from_attributes": True}


class ValveCreateRequest(BaseModel):
    name: str
    flow_rate_lpm: Decimal = Decimal("20")
    valve_type: str = "solenoid"


class ValveOpenRequest(BaseModel):
    duration_minutes: int = Field(ge=1, le=240)


class ValveScheduleUpdate(BaseModel):
    schedule: dict[str, object]


class DiseaseAlertResponse(BaseModel):
    id: uuid.UUID
    plot_id: uuid.UUID
    disease_name: str
    risk_level: str
    predicted_at: datetime
    factors: dict[str, object]
    action_recommended: str
    acknowledged_at: datetime | None
    resolved_at: datetime | None

    model_config = {"from_attributes": True}


class CalendarEntryRequest(BaseModel):
    stage: str
    started_at: datetime
    expected_end_at: datetime | None = None
    notes: str = ""


class CalendarEntryResponse(BaseModel):
    id: uuid.UUID
    farm_id: uuid.UUID
    stage: str
    started_at: datetime
    expected_end_at: datetime | None
    actual_end_at: datetime | None
    notes: str

    model_config = {"from_attributes": True}


class YieldRecordRequest(BaseModel):
    harvest_date: date
    quantity_kg: Decimal
    quality_grade: str = "A"
    price_per_kg_idr: int = 0
    buyer_name: str = ""
    notes: str = ""


class YieldRecordResponse(BaseModel):
    id: uuid.UUID
    plot_id: uuid.UUID
    harvest_date: date
    quantity_kg: Decimal
    quality_grade: str
    price_per_kg_idr: int
    total_revenue_idr: int
    buyer_name: str
    notes: str

    model_config = {"from_attributes": True}


class AnalyticsSeries(BaseModel):
    labels: list[str]
    values: list[float]


class AutoIrrigationSettings(BaseModel):
    enabled: bool = True
    moisture_threshold_pct: Decimal = Decimal("30")
