"""Alarm lifecycle tables

Revision ID: 021
Revises: 020
Create Date: 2026-10-11

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "021"
down_revision: Union[str, None] = "020"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

severity_enum = postgresql.ENUM(
    "critical",
    "major",
    "minor",
    "warning",
    "info",
    name="alarm_severity",
    create_type=False,
)
status_enum = postgresql.ENUM(
    "active",
    "acknowledged",
    "resolved",
    "cleared",
    name="alarm_status",
    create_type=False,
)
history_action_enum = postgresql.ENUM(
    "created",
    "acknowledged",
    "resolved",
    "cleared",
    "escalated",
    "commented",
    name="alarm_history_action",
    create_type=False,
)


def upgrade() -> None:
    op.execute(
        """
        DO $$ BEGIN
            CREATE TYPE alarm_severity AS ENUM (
                'critical', 'major', 'minor', 'warning', 'info'
            );
        EXCEPTION WHEN duplicate_object THEN NULL; END $$
        """
    )
    op.execute(
        """
        DO $$ BEGIN
            CREATE TYPE alarm_status AS ENUM (
                'active', 'acknowledged', 'resolved', 'cleared'
            );
        EXCEPTION WHEN duplicate_object THEN NULL; END $$
        """
    )
    op.execute(
        """
        DO $$ BEGIN
            CREATE TYPE alarm_history_action AS ENUM (
                'created', 'acknowledged', 'resolved', 'cleared', 'escalated', 'commented'
            );
        EXCEPTION WHEN duplicate_object THEN NULL; END $$
        """
    )
    op.create_table(
        "alarms",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "tenant_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("tenants.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "device_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("devices.id", ondelete="SET NULL"),
            nullable=True,
        ),
        sa.Column("alarm_type", sa.String(64), nullable=False),
        sa.Column("severity", severity_enum, nullable=False),
        sa.Column("status", status_enum, nullable=False, server_default="active"),
        sa.Column("title", sa.String(200), nullable=False),
        sa.Column("message", sa.Text(), nullable=True),
        sa.Column("details", postgresql.JSONB(), nullable=False, server_default=sa.text("'{}'::jsonb")),
        sa.Column("source", sa.String(32), nullable=False, server_default="manual"),
        sa.Column(
            "rule_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("rules.id", ondelete="SET NULL"),
            nullable=True,
        ),
        sa.Column("fingerprint", sa.String(64), nullable=False),
        sa.Column("occurred_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("acknowledged_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column(
            "acknowledged_by_user_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("users.id", ondelete="SET NULL"),
            nullable=True,
        ),
        sa.Column("resolved_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column(
            "resolved_by_user_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("users.id", ondelete="SET NULL"),
            nullable=True,
        ),
        sa.Column("cleared_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("escalation_count", sa.Integer(), nullable=False, server_default="0"),
    )
    op.create_index("ix_alarms_tenant_status", "alarms", ["tenant_id", "status"])
    op.create_index("ix_alarms_device_occurred", "alarms", ["device_id", "occurred_at"])
    op.create_index("ix_alarms_fingerprint_status", "alarms", ["fingerprint", "status"])

    op.create_table(
        "alarm_history",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "alarm_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("alarms.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("action", history_action_enum, nullable=False),
        sa.Column(
            "actor_user_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("users.id", ondelete="SET NULL"),
            nullable=True,
        ),
        sa.Column("note", sa.Text(), nullable=True),
        sa.Column(
            "occurred_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
    )
    op.create_index("ix_alarm_history_alarm_id", "alarm_history", ["alarm_id"])


def downgrade() -> None:
    op.drop_index("ix_alarm_history_alarm_id", table_name="alarm_history")
    op.drop_table("alarm_history")
    op.drop_index("ix_alarms_fingerprint_status", table_name="alarms")
    op.drop_index("ix_alarms_device_occurred", table_name="alarms")
    op.drop_index("ix_alarms_tenant_status", table_name="alarms")
    op.drop_table("alarms")
    op.execute("DROP TYPE IF EXISTS alarm_history_action")
    op.execute("DROP TYPE IF EXISTS alarm_status")
    op.execute("DROP TYPE IF EXISTS alarm_severity")
