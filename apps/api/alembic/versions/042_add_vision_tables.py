"""Vision detections and feedback

Revision ID: 042
Revises: 041
"""

from __future__ import annotations

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "042"
down_revision: str | None = "041"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "vision_detections",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("device_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("tenant_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("timestamp", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("image_url", sa.String(length=512), nullable=True),
        sa.Column("labels_json", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column("max_confidence", sa.Numeric(6, 4), nullable=False),
        sa.Column("routing_action", sa.String(length=32), nullable=False),
        sa.Column("species_guess", sa.String(length=64), nullable=False),
        sa.ForeignKeyConstraint(["device_id"], ["devices.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["tenant_id"], ["tenants.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_vision_detections_device_id", "vision_detections", ["device_id"])
    op.create_index("ix_vision_detections_tenant_id", "vision_detections", ["tenant_id"])

    op.create_table(
        "vision_feedback",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("detection_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("tenant_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("verdict", sa.String(length=32), nullable=False),
        sa.Column("notes", sa.Text(), nullable=False),
        sa.Column("verified_by", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("verified_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["detection_id"], ["vision_detections.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["tenant_id"], ["tenants.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["verified_by"], ["users.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_vision_feedback_detection_id", "vision_feedback", ["detection_id"])

    op.create_table(
        "vision_tenant_config",
        sa.Column("tenant_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("confidence_threshold", sa.Numeric(4, 3), nullable=False, server_default="0.500"),
        sa.Column("auto_trigger_enabled", sa.Boolean(), nullable=False, server_default=sa.text("true")),
        sa.ForeignKeyConstraint(["tenant_id"], ["tenants.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("tenant_id"),
    )


def downgrade() -> None:
    op.drop_table("vision_tenant_config")
    op.drop_index("ix_vision_feedback_detection_id", table_name="vision_feedback")
    op.drop_table("vision_feedback")
    op.drop_index("ix_vision_detections_tenant_id", table_name="vision_detections")
    op.drop_index("ix_vision_detections_device_id", table_name="vision_detections")
    op.drop_table("vision_detections")
