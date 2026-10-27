"""Camera gateway tables

Revision ID: 039
Revises: 038
"""

from __future__ import annotations

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "039"
down_revision: str | None = "038"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "cameras",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("tenant_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("mesh_device_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("rtsp_url", sa.String(length=1024), nullable=False),
        sa.Column("username_enc", sa.Text(), nullable=False, server_default=""),
        sa.Column("password_hash", sa.String(length=255), nullable=False, server_default=""),
        sa.Column("location", sa.String(length=512), nullable=False, server_default=""),
        sa.Column("farm_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("plot_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("physical_zone", sa.String(length=128), nullable=True),
        sa.Column("enabled", sa.Boolean(), nullable=False, server_default=sa.text("true")),
        sa.Column("last_seen_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["tenant_id"], ["tenants.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["mesh_device_id"], ["devices.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["farm_id"], ["agri_farms.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["plot_id"], ["agri_plots.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_cameras_tenant_id", "cameras", ["tenant_id"])
    op.create_index("ix_cameras_mesh_device_id", "cameras", ["mesh_device_id"])
    op.create_index("ix_cameras_farm_id", "cameras", ["farm_id"])

    op.create_table(
        "camera_snapshots",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("camera_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("captured_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("image_url", sa.String(length=1024), nullable=False),
        sa.Column("detection_json", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column("event_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["camera_id"], ["cameras.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["event_id"], ["mesh_events.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_camera_snapshots_camera_id", "camera_snapshots", ["camera_id"])
    op.create_index("ix_camera_snapshots_captured_at", "camera_snapshots", ["captured_at"])


def downgrade() -> None:
    op.drop_index("ix_camera_snapshots_captured_at", table_name="camera_snapshots")
    op.drop_index("ix_camera_snapshots_camera_id", table_name="camera_snapshots")
    op.drop_table("camera_snapshots")
    op.drop_index("ix_cameras_farm_id", table_name="cameras")
    op.drop_index("ix_cameras_mesh_device_id", table_name="cameras")
    op.drop_index("ix_cameras_tenant_id", table_name="cameras")
    op.drop_table("cameras")
