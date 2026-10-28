"""Edge device tokens and firmware versions

Revision ID: 043
Revises: 042
"""

from __future__ import annotations

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "043"
down_revision: str | None = "042"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "edge_device_tokens",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("token", sa.String(length=128), nullable=False),
        sa.Column("tenant_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("max_devices", sa.Integer(), nullable=False, server_default="100"),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["tenant_id"], ["tenants.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("token"),
    )
    op.create_index("ix_edge_device_tokens_tenant_id", "edge_device_tokens", ["tenant_id"])

    op.create_table(
        "firmware_versions",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("device_type", sa.String(length=100), nullable=False),
        sa.Column("version", sa.String(length=64), nullable=False),
        sa.Column("binary_url", sa.String(length=512), nullable=False),
        sa.Column("checksum", sa.String(length=128), nullable=False),
        sa.Column("released_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("stable", sa.Boolean(), nullable=False, server_default=sa.text("true")),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_firmware_versions_device_type", "firmware_versions", ["device_type"])


def downgrade() -> None:
    op.drop_index("ix_firmware_versions_device_type", table_name="firmware_versions")
    op.drop_table("firmware_versions")
    op.drop_index("ix_edge_device_tokens_tenant_id", table_name="edge_device_tokens")
    op.drop_table("edge_device_tokens")
