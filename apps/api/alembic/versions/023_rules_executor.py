"""Rule engine executor columns and execution log

Revision ID: 023
Revises: 022
Create Date: 2026-10-11

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "023"
down_revision: Union[str, None] = "022"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

trigger_type_enum = postgresql.ENUM(
    "telemetry",
    "attribute_change",
    "alarm",
    "schedule",
    "manual",
    name="rule_trigger_type",
    create_type=False,
)

execution_status_enum = postgresql.ENUM(
    "success",
    "error",
    "skipped",
    name="rule_execution_status",
    create_type=False,
)


def upgrade() -> None:
    bind = op.get_bind()
    trigger_type_enum.create(bind, checkfirst=True)
    execution_status_enum.create(bind, checkfirst=True)

    op.alter_column("rules", "device_id", existing_type=postgresql.UUID(as_uuid=True), nullable=True)

    op.add_column(
        "rules",
        sa.Column("enabled", sa.Boolean(), nullable=False, server_default=sa.text("true")),
    )
    op.add_column(
        "rules",
        sa.Column(
            "trigger_type",
            trigger_type_enum,
            nullable=False,
            server_default="telemetry",
        ),
    )
    op.add_column(
        "rules",
        sa.Column(
            "trigger_config",
            postgresql.JSONB(),
            nullable=False,
            server_default=sa.text("'{}'::jsonb"),
        ),
    )
    op.add_column("rules", sa.Column("condition_expr", sa.Text(), nullable=True))
    op.add_column(
        "rules",
        sa.Column(
            "actions",
            postgresql.JSONB(),
            nullable=False,
            server_default=sa.text("'[]'::jsonb"),
        ),
    )
    op.add_column("rules", sa.Column("last_executed_at", sa.DateTime(timezone=True), nullable=True))
    op.add_column(
        "rules",
        sa.Column("execution_count", sa.Integer(), nullable=False, server_default=sa.text("0")),
    )
    op.add_column("rules", sa.Column("last_error", sa.Text(), nullable=True))
    op.add_column(
        "rules",
        sa.Column("priority", sa.Integer(), nullable=False, server_default=sa.text("100")),
    )
    op.add_column(
        "rules",
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )

    op.execute(
        """
        UPDATE rules SET enabled = is_active
        """
    )
    op.execute(
        """
        UPDATE rules SET trigger_config = jsonb_build_object(
            'device_id', device_id::text,
            'metric_key', metric,
            'operator', CASE operator
                WHEN '>' THEN 'gt'
                WHEN '<' THEN 'lt'
                WHEN '>=' THEN 'gte'
                WHEN '<=' THEN 'lte'
                WHEN '==' THEN 'eq'
                ELSE 'gt'
            END,
            'threshold', threshold
        )
        WHERE trigger_config = '{}'::jsonb OR trigger_config IS NULL
        """
    )

    op.create_index("ix_rules_tenant_enabled", "rules", ["tenant_id", "enabled"])
    op.create_index("ix_rules_trigger_type", "rules", ["trigger_type"])

    op.create_table(
        "rule_execution_log",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "rule_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("rules.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("triggered_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("trigger_context", postgresql.JSONB(), nullable=False, server_default=sa.text("'{}'::jsonb")),
        sa.Column("status", execution_status_enum, nullable=False),
        sa.Column("actions_executed", sa.Integer(), nullable=False, server_default=sa.text("0")),
        sa.Column("error_message", sa.Text(), nullable=True),
        sa.Column("duration_ms", sa.Integer(), nullable=True),
    )
    op.create_index("ix_rule_execution_log_rule_triggered", "rule_execution_log", ["rule_id", "triggered_at"])
    op.create_index("ix_rule_execution_log_status_triggered", "rule_execution_log", ["status", "triggered_at"])

    op.alter_column(
        "notification_log",
        "alarm_id",
        existing_type=postgresql.UUID(as_uuid=True),
        nullable=True,
    )


def downgrade() -> None:
    op.alter_column(
        "notification_log",
        "alarm_id",
        existing_type=postgresql.UUID(as_uuid=True),
        nullable=False,
    )

    op.drop_index("ix_rule_execution_log_status_triggered", table_name="rule_execution_log")
    op.drop_index("ix_rule_execution_log_rule_triggered", table_name="rule_execution_log")
    op.drop_table("rule_execution_log")

    op.drop_index("ix_rules_trigger_type", table_name="rules")
    op.drop_index("ix_rules_tenant_enabled", table_name="rules")

    op.drop_column("rules", "updated_at")
    op.drop_column("rules", "priority")
    op.drop_column("rules", "last_error")
    op.drop_column("rules", "execution_count")
    op.drop_column("rules", "last_executed_at")
    op.drop_column("rules", "actions")
    op.drop_column("rules", "condition_expr")
    op.drop_column("rules", "trigger_config")
    op.drop_column("rules", "trigger_type")
    op.drop_column("rules", "enabled")

    op.alter_column("rules", "device_id", existing_type=postgresql.UUID(as_uuid=True), nullable=False)

    bind = op.get_bind()
    execution_status_enum.drop(bind, checkfirst=True)
    trigger_type_enum.drop(bind, checkfirst=True)
