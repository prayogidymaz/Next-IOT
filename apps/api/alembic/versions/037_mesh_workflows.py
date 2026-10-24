"""Mesh workflows + execution log

Revision ID: 037
Revises: 036
"""

from __future__ import annotations

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "037"
down_revision: str | None = "036"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "mesh_workflows",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("tenant_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("description", sa.Text(), nullable=False, server_default=""),
        sa.Column("enabled", sa.Boolean(), nullable=False, server_default=sa.text("true")),
        sa.Column("definition", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["tenant_id"], ["tenants.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_mesh_workflows_tenant_id", "mesh_workflows", ["tenant_id"])
    op.create_index("ix_mesh_workflows_enabled", "mesh_workflows", ["enabled"])

    op.create_table(
        "mesh_workflow_executions",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("tenant_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("workflow_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("trigger_event_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("status", sa.String(length=32), nullable=False),
        sa.Column("started_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("duration_ms", sa.Integer(), nullable=True),
        sa.Column("action_results", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column("error_message", sa.Text(), nullable=True),
        sa.Column("correlation_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["tenant_id"], ["tenants.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["workflow_id"], ["mesh_workflows.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["trigger_event_id"], ["mesh_events.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_mesh_workflow_executions_tenant_id", "mesh_workflow_executions", ["tenant_id"])
    op.create_index("ix_mesh_workflow_executions_workflow_id", "mesh_workflow_executions", ["workflow_id"])
    op.create_index("ix_mesh_workflow_executions_status", "mesh_workflow_executions", ["status"])
    op.create_index("ix_mesh_workflow_executions_correlation_id", "mesh_workflow_executions", ["correlation_id"])


def downgrade() -> None:
    op.drop_index("ix_mesh_workflow_executions_correlation_id", table_name="mesh_workflow_executions")
    op.drop_index("ix_mesh_workflow_executions_status", table_name="mesh_workflow_executions")
    op.drop_index("ix_mesh_workflow_executions_workflow_id", table_name="mesh_workflow_executions")
    op.drop_index("ix_mesh_workflow_executions_tenant_id", table_name="mesh_workflow_executions")
    op.drop_table("mesh_workflow_executions")
    op.drop_index("ix_mesh_workflows_enabled", table_name="mesh_workflows")
    op.drop_index("ix_mesh_workflows_tenant_id", table_name="mesh_workflows")
    op.drop_table("mesh_workflows")
