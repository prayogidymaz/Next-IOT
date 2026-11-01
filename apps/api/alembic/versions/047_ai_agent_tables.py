"""AI agent operations tables

Revision ID: 047
Revises: 046
"""

from __future__ import annotations

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "047"
down_revision: str | None = "046"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "agent_healing_suggestions",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("workflow_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("tenant_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("diagnosis_json", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column("fix_json", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column("confidence", sa.Float(), nullable=False),
        sa.Column("status", sa.String(length=32), nullable=False),
        sa.Column("applied_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("approved_by", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["approved_by"], ["users.id"]),
        sa.ForeignKeyConstraint(["tenant_id"], ["tenants.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["workflow_id"], ["mesh_workflows.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_agent_healing_suggestions_workflow_id", "agent_healing_suggestions", ["workflow_id"])
    op.create_index("ix_agent_healing_suggestions_tenant_id", "agent_healing_suggestions", ["tenant_id"])

    op.create_table(
        "agent_chain_executions",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("chain_id", sa.String(length=64), nullable=False),
        sa.Column("trigger_event_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("tenant_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("state", sa.String(length=32), nullable=False),
        sa.Column("current_step", sa.Integer(), nullable=False),
        sa.Column("context_json", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column("started_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("status", sa.String(length=32), nullable=False),
        sa.ForeignKeyConstraint(["tenant_id"], ["tenants.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_agent_chain_executions_chain_id", "agent_chain_executions", ["chain_id"])
    op.create_index("ix_agent_chain_executions_tenant_id", "agent_chain_executions", ["tenant_id"])

    op.create_table(
        "agent_alert_clusters",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("tenant_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("cluster_signature", sa.String(length=255), nullable=False),
        sa.Column("alert_ids_json", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column("risk_score", sa.Float(), nullable=False),
        sa.Column("suggested_action", sa.Text(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("resolved_at", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(["tenant_id"], ["tenants.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_agent_alert_clusters_tenant_id", "agent_alert_clusters", ["tenant_id"])
    op.create_index("ix_agent_alert_clusters_signature", "agent_alert_clusters", ["cluster_signature"])

    op.create_table(
        "agent_threshold_adjustments",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("workflow_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("tenant_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("metric", sa.String(length=64), nullable=False),
        sa.Column("old_value", sa.Float(), nullable=False),
        sa.Column("suggested_value", sa.Float(), nullable=False),
        sa.Column("reason", sa.Text(), nullable=False),
        sa.Column("status", sa.String(length=32), nullable=False),
        sa.Column("applied_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["tenant_id"], ["tenants.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["workflow_id"], ["mesh_workflows.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_agent_threshold_adjustments_workflow_id", "agent_threshold_adjustments", ["workflow_id"])

    op.create_table(
        "agent_action_feedback",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("alert_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("feedback", sa.String(length=32), nullable=False),
        sa.Column("notes", sa.Text(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["alert_id"], ["alarms.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )


def downgrade() -> None:
    op.drop_table("agent_action_feedback")
    op.drop_index("ix_agent_threshold_adjustments_workflow_id", table_name="agent_threshold_adjustments")
    op.drop_table("agent_threshold_adjustments")
    op.drop_index("ix_agent_alert_clusters_signature", table_name="agent_alert_clusters")
    op.drop_index("ix_agent_alert_clusters_tenant_id", table_name="agent_alert_clusters")
    op.drop_table("agent_alert_clusters")
    op.drop_index("ix_agent_chain_executions_tenant_id", table_name="agent_chain_executions")
    op.drop_index("ix_agent_chain_executions_chain_id", table_name="agent_chain_executions")
    op.drop_table("agent_chain_executions")
    op.drop_index("ix_agent_healing_suggestions_tenant_id", table_name="agent_healing_suggestions")
    op.drop_index("ix_agent_healing_suggestions_workflow_id", table_name="agent_healing_suggestions")
    op.drop_table("agent_healing_suggestions")
