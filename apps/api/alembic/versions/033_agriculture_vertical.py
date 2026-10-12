"""Step 11: Smart Agriculture vertical (LoRa farms, sensors, irrigation)

Revision ID: 033
Revises: 032
"""

from __future__ import annotations

import uuid
from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "033"
down_revision: str | None = "032"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

_DEMO_TENANT_ID = uuid.UUID("a3310000-0000-4000-8000-000000000033")
_DEMO_FARM_IDS = (
    uuid.UUID("a3310001-0000-4000-8000-000000000001"),
    uuid.UUID("a3310001-0000-4000-8000-000000000002"),
    uuid.UUID("a3310001-0000-4000-8000-000000000003"),
)


def _uuid_fk(
    name: str,
    target: str,
    *,
    nullable: bool = False,
    ondelete: str = "CASCADE",
) -> sa.Column:
    return sa.Column(
        name,
        postgresql.UUID(as_uuid=True),
        sa.ForeignKey(target, ondelete=ondelete),
        nullable=nullable,
    )


def upgrade() -> None:
    op.create_table(
        "agri_farms",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        _uuid_fk("tenant_id", "tenants.id"),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("crop_type", sa.String(32), nullable=False),
        sa.Column("area_hectares", sa.Numeric(10, 2), nullable=False, server_default="0"),
        sa.Column("location_lat", sa.Numeric(10, 7), nullable=True),
        sa.Column("location_lng", sa.Numeric(10, 7), nullable=True),
        sa.Column("location_address", sa.Text(), nullable=False, server_default=""),
        sa.Column("planted_date", sa.Date(), nullable=True),
        sa.Column("expected_harvest_date", sa.Date(), nullable=True),
        sa.Column("owner_name", sa.String(255), nullable=False, server_default=""),
        sa.Column("owner_phone", sa.String(32), nullable=False, server_default=""),
        sa.Column("owner_whatsapp", sa.String(32), nullable=False, server_default=""),
        sa.Column("metadata", postgresql.JSONB(), nullable=False, server_default="{}"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_index("ix_agri_farms_tenant_id", "agri_farms", ["tenant_id"])

    op.create_table(
        "agri_plots",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        _uuid_fk("farm_id", "agri_farms.id"),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("polygon", postgresql.JSONB(), nullable=False, server_default="{}"),
        sa.Column("area_hectares", sa.Numeric(10, 2), nullable=False, server_default="0"),
        sa.Column("crop_variety", sa.String(128), nullable=False, server_default=""),
        sa.Column("planted_count", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("notes", sa.Text(), nullable=False, server_default=""),
    )
    op.create_index("ix_agri_plots_farm_id", "agri_plots", ["farm_id"])

    op.create_table(
        "agri_lora_gateways",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        _uuid_fk("tenant_id", "tenants.id"),
        _uuid_fk("farm_id", "agri_farms.id"),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("gateway_eui", sa.String(16), nullable=False, unique=True),
        sa.Column("position_lat", sa.Numeric(10, 7), nullable=True),
        sa.Column("position_lng", sa.Numeric(10, 7), nullable=True),
        sa.Column("position_altitude_m", sa.Integer(), nullable=True),
        sa.Column("antenna_type", sa.String(64), nullable=False, server_default="fiberglass"),
        sa.Column("antenna_gain_dbi", sa.Numeric(3, 1), nullable=False, server_default="3.0"),
        sa.Column("uplink_channel", sa.String(16), nullable=False, server_default="ethernet"),
        sa.Column("status", sa.String(16), nullable=False, server_default="offline"),
        sa.Column("last_seen_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("firmware_version", sa.String(64), nullable=False, server_default=""),
        sa.Column("packets_rx_total", sa.BigInteger(), nullable=False, server_default="0"),
        sa.Column("packets_tx_total", sa.BigInteger(), nullable=False, server_default="0"),
    )

    op.create_table(
        "agri_sensor_devices",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        _uuid_fk("tenant_id", "tenants.id"),
        _uuid_fk("farm_id", "agri_farms.id"),
        _uuid_fk("plot_id", "agri_plots.id", nullable=True, ondelete="SET NULL"),
        _uuid_fk("device_id", "devices.id", nullable=True, ondelete="SET NULL"),
        sa.Column("name", sa.String(255), nullable=False, server_default=""),
        sa.Column("sensor_type", sa.String(32), nullable=False),
        sa.Column("lora_dev_eui", sa.String(16), nullable=False),
        sa.Column("lora_app_key_enc", sa.Text(), nullable=False, server_default=""),
        sa.Column("position_lat", sa.Numeric(10, 7), nullable=True),
        sa.Column("position_lng", sa.Numeric(10, 7), nullable=True),
        sa.Column("position_depth_cm", sa.Integer(), nullable=True),
        sa.Column("installed_date", sa.Date(), nullable=True),
        sa.Column("battery_installed_date", sa.Date(), nullable=True),
        sa.Column("last_battery_voltage", sa.Numeric(3, 2), nullable=True),
        sa.Column("last_rssi", sa.Integer(), nullable=True),
        sa.Column("last_snr", sa.Numeric(3, 1), nullable=True),
        sa.Column("firmware_version", sa.String(64), nullable=False, server_default=""),
        sa.Column("calibration_data", postgresql.JSONB(), nullable=False, server_default="{}"),
    )
    op.create_index("ix_agri_sensor_devices_farm_id", "agri_sensor_devices", ["farm_id"])
    op.create_index("ix_agri_sensor_devices_lora_dev_eui", "agri_sensor_devices", ["lora_dev_eui"], unique=True)

    op.create_table(
        "agri_irrigation_valves",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        _uuid_fk("farm_id", "agri_farms.id"),
        _uuid_fk("plot_id", "agri_plots.id"),
        _uuid_fk("device_id", "devices.id", nullable=True, ondelete="SET NULL"),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("position_lat", sa.Numeric(10, 7), nullable=True),
        sa.Column("position_lng", sa.Numeric(10, 7), nullable=True),
        sa.Column("valve_type", sa.String(32), nullable=False, server_default="solenoid"),
        sa.Column("flow_rate_lpm", sa.Numeric(10, 2), nullable=False, server_default="0"),
        sa.Column("current_state", sa.String(16), nullable=False, server_default="closed"),
        sa.Column("last_opened_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("last_closed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("total_opens_count", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("schedule", postgresql.JSONB(), nullable=False, server_default="{}"),
        sa.Column("auto_irrigation_enabled", sa.Boolean(), nullable=False, server_default="false"),
        sa.Column("moisture_threshold_pct", sa.Numeric(5, 2), nullable=False, server_default="30"),
    )

    op.create_table(
        "agri_irrigation_logs",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        _uuid_fk("farm_id", "agri_farms.id"),
        _uuid_fk("plot_id", "agri_plots.id", nullable=True, ondelete="SET NULL"),
        _uuid_fk("valve_id", "agri_irrigation_valves.id", nullable=True, ondelete="SET NULL"),
        sa.Column("action", sa.String(32), nullable=False),
        sa.Column("duration_minutes", sa.Integer(), nullable=True),
        sa.Column("trigger", sa.String(32), nullable=False, server_default="manual"),
        sa.Column("detail", postgresql.JSONB(), nullable=False, server_default="{}"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )

    op.create_table(
        "agri_disease_alerts",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        _uuid_fk("plot_id", "agri_plots.id"),
        sa.Column("disease_name", sa.String(255), nullable=False),
        sa.Column("risk_level", sa.String(16), nullable=False),
        sa.Column("predicted_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("factors", postgresql.JSONB(), nullable=False, server_default="{}"),
        sa.Column("action_recommended", sa.Text(), nullable=False, server_default=""),
        sa.Column("acknowledged_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("resolved_at", sa.DateTime(timezone=True), nullable=True),
    )

    op.create_table(
        "agri_crop_calendar",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        _uuid_fk("farm_id", "agri_farms.id"),
        sa.Column("stage", sa.String(32), nullable=False),
        sa.Column("started_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("expected_end_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("actual_end_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("notes", sa.Text(), nullable=False, server_default=""),
    )

    op.create_table(
        "agri_yield_records",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        _uuid_fk("plot_id", "agri_plots.id"),
        sa.Column("harvest_date", sa.Date(), nullable=False),
        sa.Column("quantity_kg", sa.Numeric(12, 2), nullable=False),
        sa.Column("quality_grade", sa.String(8), nullable=False, server_default="A"),
        sa.Column("price_per_kg_idr", sa.BigInteger(), nullable=False, server_default="0"),
        sa.Column("total_revenue_idr", sa.BigInteger(), nullable=False, server_default="0"),
        sa.Column("buyer_name", sa.String(255), nullable=False, server_default=""),
        sa.Column("notes", sa.Text(), nullable=False, server_default=""),
    )

    op.create_table(
        "agri_sensor_battery_history",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        _uuid_fk("sensor_id", "agri_sensor_devices.id"),
        sa.Column("voltage", sa.Numeric(3, 2), nullable=False),
        sa.Column("recorded_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )

    _seed_demo_farms()


def _seed_demo_farms() -> None:
    bind = op.get_bind()
    exists = bind.execute(sa.text("SELECT 1 FROM tenants WHERE id = :id"), {"id": str(_DEMO_TENANT_ID)}).fetchone()
    if exists is None:
        bind.execute(
            sa.text(
                """
                INSERT INTO tenants (id, name, slug, security_tier, is_active)
                VALUES (:id, 'Next-IoT Agri Demo', 'next-iot-agri-demo', 'pro', true)
                ON CONFLICT (slug) DO NOTHING
                """
            ),
            {"id": str(_DEMO_TENANT_ID)},
        )
    farms = [
        (_DEMO_FARM_IDS[0], "Kebun Kopi Toraja Blok A", "coffee", -3.0738, 119.8707, "Toraja, Sulawesi Selatan"),
        (_DEMO_FARM_IDS[1], "Perkebunan Sawit Riau", "oil_palm", 0.5071, 101.4478, "Pekanbaru, Riau"),
        (_DEMO_FARM_IDS[2], "Sawah Padi Jawa Tengah", "rice", -7.1500, 110.1400, "Klaten, Jawa Tengah"),
    ]
    for farm_id, name, crop, lat, lng, addr in farms:
        bind.execute(
            sa.text(
                """
                INSERT INTO agri_farms (
                    id, tenant_id, name, crop_type, area_hectares, location_lat, location_lng,
                    location_address, owner_name, owner_whatsapp
                )
                VALUES (
                    :id, :tenant_id, :name, :crop, 12.5, :lat, :lng, :addr,
                    'Demo Petani', '6281234567890'
                )
                ON CONFLICT (id) DO NOTHING
                """
            ),
            {
                "id": str(farm_id),
                "tenant_id": str(_DEMO_TENANT_ID),
                "name": name,
                "crop": crop,
                "lat": lat,
                "lng": lng,
                "addr": addr,
            },
        )


def downgrade() -> None:
    op.drop_table("agri_sensor_battery_history")
    op.drop_table("agri_yield_records")
    op.drop_table("agri_crop_calendar")
    op.drop_table("agri_disease_alerts")
    op.drop_table("agri_irrigation_logs")
    op.drop_table("agri_irrigation_valves")
    op.drop_table("agri_sensor_devices")
    op.drop_table("agri_lora_gateways")
    op.drop_table("agri_plots")
    op.drop_table("agri_farms")
    bind = op.get_bind()
    bind.execute(sa.text("DELETE FROM tenants WHERE slug = 'next-iot-agri-demo'"))
