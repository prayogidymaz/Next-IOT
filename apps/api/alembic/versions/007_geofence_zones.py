"""Geofence zones table

Revision ID: 007
Revises: 006
Create Date: 2026-09-12

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "007"
down_revision: Union[str, None] = "006"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "geofence_zones",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("tenant_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False),
        sa.Column("name", sa.String(128), nullable=False),
        sa.Column("polygon_coords", postgresql.JSONB(), nullable=False),
        sa.Column("max_altitude", sa.Float(), nullable=False, server_default="120"),
        sa.Column("min_altitude", sa.Float(), nullable=False, server_default="0"),
        sa.Column("action_on_breach", sa.String(8), nullable=False, server_default="WARN"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_index("ix_geofence_zones_tenant_id", "geofence_zones", ["tenant_id"])


def downgrade() -> None:
    op.drop_table("geofence_zones")
