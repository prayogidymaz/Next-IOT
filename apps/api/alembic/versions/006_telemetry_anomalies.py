"""Telemetry anomalies log table

Revision ID: 006
Revises: 005
Create Date: 2026-09-10

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "006"
down_revision: Union[str, None] = "005"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "telemetry_anomalies",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("device_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("devices.id", ondelete="CASCADE"), nullable=False),
        sa.Column("tenant_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False),
        sa.Column("reading_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("telemetry_readings.id", ondelete="SET NULL"), nullable=True),
        sa.Column("severity", sa.String(20), nullable=False),
        sa.Column("anomaly_type", sa.String(64), nullable=False),
        sa.Column("message", sa.Text(), nullable=False),
        sa.Column("metadata", postgresql.JSONB(), nullable=False, server_default=sa.text("'{}'::jsonb")),
        sa.Column("recorded_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("detected_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_index("ix_telemetry_anomalies_device_id", "telemetry_anomalies", ["device_id"])
    op.create_index("ix_telemetry_anomalies_tenant_id", "telemetry_anomalies", ["tenant_id"])
    op.create_index("ix_telemetry_anomalies_severity", "telemetry_anomalies", ["severity"])
    op.create_index("ix_telemetry_anomalies_anomaly_type", "telemetry_anomalies", ["anomaly_type"])
    op.create_index("ix_telemetry_anomalies_recorded_at", "telemetry_anomalies", ["recorded_at"])


def downgrade() -> None:
    op.drop_table("telemetry_anomalies")
