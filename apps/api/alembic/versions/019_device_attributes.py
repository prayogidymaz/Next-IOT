"""Device attributes (server / shared / client scopes)

Revision ID: 019
Revises: 017
Create Date: 2026-10-10

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "019"
down_revision: Union[str, None] = "017"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

scope_enum = postgresql.ENUM(
    "server",
    "shared",
    "client",
    name="device_attribute_scope",
    create_type=False,
)


def upgrade() -> None:
    op.execute(
        """
        DO $$ BEGIN
            CREATE TYPE device_attribute_scope AS ENUM ('server', 'shared', 'client');
        EXCEPTION
            WHEN duplicate_object THEN NULL;
        END $$
        """
    )
    op.create_table(
        "device_attributes",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "device_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("devices.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "tenant_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("tenants.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("scope", scope_enum, nullable=False),
        sa.Column("key", sa.String(128), nullable=False),
        sa.Column("value_json", postgresql.JSONB(), nullable=False),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.Column(
            "updated_by_user_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("users.id", ondelete="SET NULL"),
            nullable=True,
        ),
        sa.Column("updated_source", sa.String(32), server_default="api", nullable=False),
        sa.UniqueConstraint("device_id", "scope", "key", name="uq_device_attributes_device_scope_key"),
    )
    op.create_index("ix_device_attributes_tenant_scope", "device_attributes", ["tenant_id", "scope"])
    op.create_index("ix_device_attributes_device_id", "device_attributes", ["device_id"])


def downgrade() -> None:
    op.drop_index("ix_device_attributes_device_id", table_name="device_attributes")
    op.drop_index("ix_device_attributes_tenant_scope", table_name="device_attributes")
    op.drop_table("device_attributes")
    op.execute("DROP TYPE IF EXISTS device_attribute_scope")
