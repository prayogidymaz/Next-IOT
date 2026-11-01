"""AI decision engine tables

Revision ID: 055
Revises: 054
"""

from __future__ import annotations

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "055"
down_revision: str | None = "054"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "decision_recommendations",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("tenant_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("context_json", postgresql.JSONB(astext_type=sa.Text()), nullable=False, server_default=sa.text("'{}'::jsonb")),
        sa.Column("recommendation_type", sa.String(length=64), nullable=False),
        sa.Column("confidence", sa.Float(), nullable=False, server_default="0"),
        sa.Column("status", sa.String(length=32), nullable=False, server_default="pending"),
        sa.Column("applied_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("outcome_json", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["tenant_id"], ["tenants.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_decision_recommendations_tenant", "decision_recommendations", ["tenant_id"])

    op.create_table(
        "auto_action_policies",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("tenant_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("trigger_type", sa.String(length=64), nullable=False),
        sa.Column("min_confidence", sa.Float(), nullable=False, server_default="0.8"),
        sa.Column("auto_apply", sa.Boolean(), nullable=False, server_default=sa.text("false")),
        sa.Column("approval_required", sa.Boolean(), nullable=False, server_default=sa.text("true")),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["tenant_id"], ["tenants.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )


def downgrade() -> None:
    op.drop_table("auto_action_policies")
    op.drop_index("ix_decision_recommendations_tenant", table_name="decision_recommendations")
    op.drop_table("decision_recommendations")
