"""Firmware releases and OTA rollout tracking

Revision ID: 011
Revises: 010
Create Date: 2026-09-17

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects.postgresql import UUID

revision: str = "011"
down_revision: Union[str, None] = "010"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "firmware_releases",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("tenant_id", UUID(as_uuid=True), sa.ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False),
        sa.Column("version", sa.String(length=64), nullable=False),
        sa.Column("target_device_category", sa.String(length=64), nullable=False),
        sa.Column("file_url", sa.String(length=512), nullable=False),
        sa.Column("checksum_sha256", sa.String(length=64), nullable=False),
        sa.Column("status", sa.String(length=32), nullable=False, server_default="draft"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index("ix_firmware_releases_tenant_id", "firmware_releases", ["tenant_id"])
    op.create_index(
        "ix_firmware_releases_tenant_category_status",
        "firmware_releases",
        ["tenant_id", "target_device_category", "status"],
    )

    op.create_table(
        "ota_device_rollouts",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("tenant_id", UUID(as_uuid=True), sa.ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False),
        sa.Column(
            "release_id",
            UUID(as_uuid=True),
            sa.ForeignKey("firmware_releases.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("device_id", UUID(as_uuid=True), sa.ForeignKey("devices.id", ondelete="CASCADE"), nullable=False),
        sa.Column("status", sa.String(length=32), nullable=False, server_default="pending"),
        sa.Column("reported_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.UniqueConstraint("release_id", "device_id", name="uq_ota_rollout_release_device"),
    )
    op.create_index("ix_ota_device_rollouts_release_id", "ota_device_rollouts", ["release_id"])
    op.create_index("ix_ota_device_rollouts_device_id", "ota_device_rollouts", ["device_id"])


def downgrade() -> None:
    op.drop_table("ota_device_rollouts")
    op.drop_table("firmware_releases")
