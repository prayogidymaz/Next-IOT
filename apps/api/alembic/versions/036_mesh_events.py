"""Mesh events audit log

Revision ID: 036
Revises: 035
"""

from __future__ import annotations

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "036"
down_revision: str | None = "035"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "mesh_events",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("tenant_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("device_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("domain", sa.String(length=32), nullable=False),
        sa.Column("event_type", sa.String(length=64), nullable=False),
        sa.Column("timestamp", sa.DateTime(timezone=True), nullable=False),
        sa.Column("payload", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column("context", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column("correlation_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("parent_event_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["device_id"], ["devices.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["parent_event_id"], ["mesh_events.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["tenant_id"], ["tenants.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_mesh_events_tenant_id", "mesh_events", ["tenant_id"])
    op.create_index("ix_mesh_events_device_id", "mesh_events", ["device_id"])
    op.create_index("ix_mesh_events_domain", "mesh_events", ["domain"])
    op.create_index("ix_mesh_events_event_type", "mesh_events", ["event_type"])
    op.create_index("ix_mesh_events_timestamp", "mesh_events", ["timestamp"])
    op.create_index("ix_mesh_events_correlation_id", "mesh_events", ["correlation_id"])
    op.create_index("ix_mesh_events_parent_event_id", "mesh_events", ["parent_event_id"])
    op.create_index(
        "ix_mesh_events_tenant_domain_type_ts",
        "mesh_events",
        ["tenant_id", "domain", "event_type", sa.text("timestamp DESC")],
    )


def downgrade() -> None:
    op.drop_index("ix_mesh_events_tenant_domain_type_ts", table_name="mesh_events")
    op.drop_index("ix_mesh_events_parent_event_id", table_name="mesh_events")
    op.drop_index("ix_mesh_events_correlation_id", table_name="mesh_events")
    op.drop_index("ix_mesh_events_timestamp", table_name="mesh_events")
    op.drop_index("ix_mesh_events_event_type", table_name="mesh_events")
    op.drop_index("ix_mesh_events_domain", table_name="mesh_events")
    op.drop_index("ix_mesh_events_device_id", table_name="mesh_events")
    op.drop_index("ix_mesh_events_tenant_id", table_name="mesh_events")
    op.drop_table("mesh_events")
