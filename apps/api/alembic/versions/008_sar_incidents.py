"""SAR incidents table

Revision ID: 008
Revises: 007
Create Date: 2026-09-12

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "008"
down_revision: Union[str, None] = "007"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "sar_incidents",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("tenant_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False),
        sa.Column("incident_type", sa.String(32), nullable=False),
        sa.Column("status", sa.String(16), nullable=False, server_default="ACTIVE"),
        sa.Column("target_lat", sa.Float(), nullable=False),
        sa.Column("target_lon", sa.Float(), nullable=False),
        sa.Column("severity", sa.String(16), nullable=False, server_default="critical"),
        sa.Column("assigned_device_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("devices.id", ondelete="SET NULL"), nullable=True),
        sa.Column("message", sa.Text(), nullable=True),
        sa.Column("sar_grid", postgresql.JSONB(), nullable=False, server_default=sa.text("'{}'::jsonb")),
        sa.Column("metadata", postgresql.JSONB(), nullable=False, server_default=sa.text("'{}'::jsonb")),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("resolved_at", sa.DateTime(timezone=True), nullable=True),
    )
    op.create_index("ix_sar_incidents_tenant_id", "sar_incidents", ["tenant_id"])
    op.create_index("ix_sar_incidents_status", "sar_incidents", ["status"])
    op.create_index("ix_sar_incidents_incident_type", "sar_incidents", ["incident_type"])
    op.create_index("ix_sar_incidents_assigned_device_id", "sar_incidents", ["assigned_device_id"])


def downgrade() -> None:
    op.drop_table("sar_incidents")
