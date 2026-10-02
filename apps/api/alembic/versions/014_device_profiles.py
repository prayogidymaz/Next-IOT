"""Device profiles (thing model) and device.profile_id

Revision ID: 014
Revises: 013
Create Date: 2026-10-02

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects.postgresql import JSONB, UUID

revision: str = "014"
down_revision: Union[str, None] = "013"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "device_profiles",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("tenant_id", UUID(as_uuid=True), sa.ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False),
        sa.Column("key", sa.String(length=64), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("description", sa.Text(), nullable=False, server_default=""),
        sa.Column("domain", sa.String(length=32), nullable=False),
        sa.Column("version", sa.Integer(), nullable=False, server_default="1"),
        sa.Column("status", sa.String(length=16), nullable=False, server_default="draft"),
        sa.Column("spec", JSONB(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.UniqueConstraint("tenant_id", "key", "version", name="uq_device_profiles_tenant_key_version"),
    )
    op.create_index("ix_device_profiles_tenant_id", "device_profiles", ["tenant_id"])

    op.add_column("devices", sa.Column("profile_id", UUID(as_uuid=True), nullable=True))
    op.create_foreign_key(
        "fk_devices_profile_id",
        "devices",
        "device_profiles",
        ["profile_id"],
        ["id"],
        ondelete="RESTRICT",
    )
    op.create_index("ix_devices_profile_id", "devices", ["profile_id"])


def downgrade() -> None:
    op.drop_index("ix_devices_profile_id", table_name="devices")
    op.drop_constraint("fk_devices_profile_id", "devices", type_="foreignkey")
    op.drop_column("devices", "profile_id")
    op.drop_index("ix_device_profiles_tenant_id", table_name="device_profiles")
    op.drop_table("device_profiles")
