"""Device RPC two-way command requests

Revision ID: 020
Revises: 019
Create Date: 2026-10-10

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "020"
down_revision: Union[str, None] = "019"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

rpc_status_enum = postgresql.ENUM(
    "pending",
    "delivered",
    "completed",
    "timeout",
    "failed",
    name="device_rpc_status",
    create_type=False,
)


def upgrade() -> None:
    op.execute(
        """
        DO $$ BEGIN
            CREATE TYPE device_rpc_status AS ENUM (
                'pending', 'delivered', 'completed', 'timeout', 'failed'
            );
        EXCEPTION
            WHEN duplicate_object THEN NULL;
        END $$
        """
    )
    op.create_table(
        "device_rpc_requests",
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
        sa.Column("method", sa.String(64), nullable=False),
        sa.Column("params", postgresql.JSONB(), nullable=False, server_default=sa.text("'{}'::jsonb")),
        sa.Column("status", rpc_status_enum, nullable=False, server_default="pending"),
        sa.Column("response_json", postgresql.JSONB(), nullable=True),
        sa.Column("error_message", sa.Text(), nullable=True),
        sa.Column("timeout_seconds", sa.Integer(), nullable=False, server_default="30"),
        sa.Column(
            "requested_by_user_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("users.id", ondelete="SET NULL"),
            nullable=True,
        ),
        sa.Column(
            "requested_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.Column("delivered_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
    )
    op.create_index(
        "ix_device_rpc_requests_device_status",
        "device_rpc_requests",
        ["device_id", "status"],
    )
    op.create_index("ix_device_rpc_requests_requested_at", "device_rpc_requests", ["requested_at"])


def downgrade() -> None:
    op.drop_index("ix_device_rpc_requests_requested_at", table_name="device_rpc_requests")
    op.drop_index("ix_device_rpc_requests_device_status", table_name="device_rpc_requests")
    op.drop_table("device_rpc_requests")
    op.execute("DROP TYPE IF EXISTS device_rpc_status")
