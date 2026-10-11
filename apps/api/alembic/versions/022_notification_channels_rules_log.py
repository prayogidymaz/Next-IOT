"""Notification channels, rules, and delivery log

Revision ID: 022
Revises: 021
Create Date: 2026-10-11

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "022"
down_revision: Union[str, None] = "021"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

channel_type_enum = postgresql.ENUM(
    "whatsapp",
    "telegram",
    "fcm",
    "email",
    "sms",
    name="notification_channel_type",
    create_type=False,
)
log_status_enum = postgresql.ENUM(
    "pending",
    "sent",
    "delivered",
    "failed",
    name="notification_log_status",
    create_type=False,
)


def upgrade() -> None:
    op.execute(
        """
        DO $$ BEGIN
            CREATE TYPE notification_channel_type AS ENUM (
                'whatsapp', 'telegram', 'fcm', 'email', 'sms'
            );
        EXCEPTION WHEN duplicate_object THEN NULL; END $$
        """
    )
    op.execute(
        """
        DO $$ BEGIN
            CREATE TYPE notification_log_status AS ENUM (
                'pending', 'sent', 'delivered', 'failed'
            );
        EXCEPTION WHEN duplicate_object THEN NULL; END $$
        """
    )
    op.create_table(
        "notification_channels",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "tenant_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("tenants.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("channel_type", channel_type_enum, nullable=False),
        sa.Column("name", sa.String(100), nullable=False),
        sa.Column("config", postgresql.JSONB(), nullable=False, server_default=sa.text("'{}'::jsonb")),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.text("true")),
        sa.Column(
            "created_by_user_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("users.id", ondelete="SET NULL"),
            nullable=True,
        ),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_index("ix_notification_channels_tenant", "notification_channels", ["tenant_id"])

    op.create_table(
        "notification_rules",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "tenant_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("tenants.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("name", sa.String(100), nullable=False),
        sa.Column("alarm_filter", postgresql.JSONB(), nullable=False, server_default=sa.text("'{}'::jsonb")),
        sa.Column("channel_ids", postgresql.ARRAY(postgresql.UUID(as_uuid=True)), nullable=False),
        sa.Column("throttle_seconds", sa.Integer(), nullable=False, server_default="60"),
        sa.Column("escalation_minutes", sa.Integer(), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.text("true")),
    )
    op.create_index("ix_notification_rules_tenant", "notification_rules", ["tenant_id"])

    op.create_table(
        "notification_log",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "alarm_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("alarms.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "channel_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("notification_channels.id", ondelete="SET NULL"),
            nullable=True,
        ),
        sa.Column("channel_type", sa.String(32), nullable=False),
        sa.Column("status", log_status_enum, nullable=False, server_default="pending"),
        sa.Column("provider_response", postgresql.JSONB(), nullable=True),
        sa.Column("sent_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("delivered_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("error_message", sa.Text(), nullable=True),
        sa.Column("retry_count", sa.Integer(), nullable=False, server_default="0"),
    )
    op.create_index("ix_notification_log_alarm", "notification_log", ["alarm_id"])


def downgrade() -> None:
    op.drop_index("ix_notification_log_alarm", table_name="notification_log")
    op.drop_table("notification_log")
    op.drop_index("ix_notification_rules_tenant", table_name="notification_rules")
    op.drop_table("notification_rules")
    op.drop_index("ix_notification_channels_tenant", table_name="notification_channels")
    op.drop_table("notification_channels")
    op.execute("DROP TYPE IF EXISTS notification_log_status")
    op.execute("DROP TYPE IF EXISTS notification_channel_type")
