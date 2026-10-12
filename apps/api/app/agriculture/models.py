"""SQLAlchemy models for Smart Agriculture vertical."""

from __future__ import annotations

import uuid
from datetime import date, datetime
from decimal import Decimal

from sqlalchemy import BigInteger, Boolean, Date, DateTime, ForeignKey, Integer, Numeric, String, Text, func
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class AgriFarm(Base):
    __tablename__ = "agri_farms"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("tenants.id", ondelete="CASCADE"))
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    crop_type: Mapped[str] = mapped_column(String(32), nullable=False)
    area_hectares: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False, default=Decimal("0"))
    location_lat: Mapped[Decimal | None] = mapped_column(Numeric(10, 7), nullable=True)
    location_lng: Mapped[Decimal | None] = mapped_column(Numeric(10, 7), nullable=True)
    location_address: Mapped[str] = mapped_column(Text, nullable=False, default="")
    planted_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    expected_harvest_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    owner_name: Mapped[str] = mapped_column(String(255), nullable=False, default="")
    owner_phone: Mapped[str] = mapped_column(String(32), nullable=False, default="")
    owner_whatsapp: Mapped[str] = mapped_column(String(32), nullable=False, default="")
    metadata_json: Mapped[dict[str, object]] = mapped_column("metadata", JSONB, nullable=False, default=dict)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )


class AgriPlot(Base):
    __tablename__ = "agri_plots"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    farm_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("agri_farms.id", ondelete="CASCADE"))
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    polygon: Mapped[dict[str, object]] = mapped_column(JSONB, nullable=False, default=dict)
    area_hectares: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False, default=Decimal("0"))
    crop_variety: Mapped[str] = mapped_column(String(128), nullable=False, default="")
    planted_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    notes: Mapped[str] = mapped_column(Text, nullable=False, default="")


class AgriLoraGateway(Base):
    __tablename__ = "agri_lora_gateways"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("tenants.id", ondelete="CASCADE"))
    farm_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("agri_farms.id", ondelete="CASCADE"))
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    gateway_eui: Mapped[str] = mapped_column(String(16), nullable=False, unique=True)
    position_lat: Mapped[Decimal | None] = mapped_column(Numeric(10, 7), nullable=True)
    position_lng: Mapped[Decimal | None] = mapped_column(Numeric(10, 7), nullable=True)
    position_altitude_m: Mapped[int | None] = mapped_column(Integer, nullable=True)
    antenna_type: Mapped[str] = mapped_column(String(64), nullable=False, default="fiberglass")
    antenna_gain_dbi: Mapped[Decimal] = mapped_column(Numeric(3, 1), nullable=False, default=Decimal("3.0"))
    uplink_channel: Mapped[str] = mapped_column(String(16), nullable=False, default="ethernet")
    status: Mapped[str] = mapped_column(String(16), nullable=False, default="offline")
    last_seen_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    firmware_version: Mapped[str] = mapped_column(String(64), nullable=False, default="")
    packets_rx_total: Mapped[int] = mapped_column(BigInteger, nullable=False, default=0)
    packets_tx_total: Mapped[int] = mapped_column(BigInteger, nullable=False, default=0)


class AgriSensorDevice(Base):
    __tablename__ = "agri_sensor_devices"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("tenants.id", ondelete="CASCADE"))
    farm_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("agri_farms.id", ondelete="CASCADE"))
    plot_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("agri_plots.id", ondelete="SET NULL"), nullable=True
    )
    device_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("devices.id", ondelete="SET NULL"), nullable=True
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False, default="")
    sensor_type: Mapped[str] = mapped_column(String(32), nullable=False)
    lora_dev_eui: Mapped[str] = mapped_column(String(16), nullable=False, unique=True)
    lora_app_key_enc: Mapped[str] = mapped_column(Text, nullable=False, default="")
    position_lat: Mapped[Decimal | None] = mapped_column(Numeric(10, 7), nullable=True)
    position_lng: Mapped[Decimal | None] = mapped_column(Numeric(10, 7), nullable=True)
    position_depth_cm: Mapped[int | None] = mapped_column(Integer, nullable=True)
    installed_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    battery_installed_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    last_battery_voltage: Mapped[Decimal | None] = mapped_column(Numeric(3, 2), nullable=True)
    last_rssi: Mapped[int | None] = mapped_column(Integer, nullable=True)
    last_snr: Mapped[Decimal | None] = mapped_column(Numeric(3, 1), nullable=True)
    firmware_version: Mapped[str] = mapped_column(String(64), nullable=False, default="")
    calibration_data: Mapped[dict[str, object]] = mapped_column(JSONB, nullable=False, default=dict)


class AgriIrrigationValve(Base):
    __tablename__ = "agri_irrigation_valves"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    farm_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("agri_farms.id", ondelete="CASCADE"))
    plot_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("agri_plots.id", ondelete="CASCADE"))
    device_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("devices.id", ondelete="SET NULL"), nullable=True
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    position_lat: Mapped[Decimal | None] = mapped_column(Numeric(10, 7), nullable=True)
    position_lng: Mapped[Decimal | None] = mapped_column(Numeric(10, 7), nullable=True)
    valve_type: Mapped[str] = mapped_column(String(32), nullable=False, default="solenoid")
    flow_rate_lpm: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False, default=Decimal("0"))
    current_state: Mapped[str] = mapped_column(String(16), nullable=False, default="closed")
    last_opened_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    last_closed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    total_opens_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    schedule: Mapped[dict[str, object]] = mapped_column(JSONB, nullable=False, default=dict)
    auto_irrigation_enabled: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    moisture_threshold_pct: Mapped[Decimal] = mapped_column(Numeric(5, 2), nullable=False, default=Decimal("30"))


class AgriIrrigationLog(Base):
    __tablename__ = "agri_irrigation_logs"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    farm_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("agri_farms.id", ondelete="CASCADE"))
    plot_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("agri_plots.id", ondelete="SET NULL"), nullable=True
    )
    valve_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("agri_irrigation_valves.id", ondelete="SET NULL"), nullable=True
    )
    action: Mapped[str] = mapped_column(String(32), nullable=False)
    duration_minutes: Mapped[int | None] = mapped_column(Integer, nullable=True)
    trigger: Mapped[str] = mapped_column(String(32), nullable=False, default="manual")
    detail: Mapped[dict[str, object]] = mapped_column(JSONB, nullable=False, default=dict)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


class AgriDiseaseAlert(Base):
    __tablename__ = "agri_disease_alerts"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    plot_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("agri_plots.id", ondelete="CASCADE"))
    disease_name: Mapped[str] = mapped_column(String(255), nullable=False)
    risk_level: Mapped[str] = mapped_column(String(16), nullable=False)
    predicted_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    factors: Mapped[dict[str, object]] = mapped_column(JSONB, nullable=False, default=dict)
    action_recommended: Mapped[str] = mapped_column(Text, nullable=False, default="")
    acknowledged_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    resolved_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    notified_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    snoozed_until: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)


class AgriCropCalendar(Base):
    __tablename__ = "agri_crop_calendar"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    farm_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("agri_farms.id", ondelete="CASCADE"))
    stage: Mapped[str] = mapped_column(String(32), nullable=False)
    started_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    expected_end_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    actual_end_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    notes: Mapped[str] = mapped_column(Text, nullable=False, default="")


class AgriYieldRecord(Base):
    __tablename__ = "agri_yield_records"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    plot_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("agri_plots.id", ondelete="CASCADE"))
    harvest_date: Mapped[date] = mapped_column(Date, nullable=False)
    quantity_kg: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    quality_grade: Mapped[str] = mapped_column(String(8), nullable=False, default="A")
    price_per_kg_idr: Mapped[int] = mapped_column(BigInteger, nullable=False, default=0)
    total_revenue_idr: Mapped[int] = mapped_column(BigInteger, nullable=False, default=0)
    buyer_name: Mapped[str] = mapped_column(String(255), nullable=False, default="")
    notes: Mapped[str] = mapped_column(Text, nullable=False, default="")


class AgriSensorBatteryHistory(Base):
    __tablename__ = "agri_sensor_battery_history"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    sensor_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("agri_sensor_devices.id", ondelete="CASCADE")
    )
    voltage: Mapped[Decimal] = mapped_column(Numeric(3, 2), nullable=False)
    recorded_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
