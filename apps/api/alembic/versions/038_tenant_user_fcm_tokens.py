"""tenant_user_fcm_tokens for workflow FCM push

Revision ID: 038
Revises: 037
"""

from __future__ import annotations

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "038"
down_revision: str | None = "037"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "tenant_user_fcm_tokens",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("tenant_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("token", sa.String(length=512), nullable=False),
        sa.Column("device_type", sa.String(length=64), nullable=False, server_default="wear"),
        sa.Column("last_seen_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["tenant_id"], ["tenants.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("token", name="uq_tenant_user_fcm_tokens_token"),
    )
    op.create_index("ix_tenant_user_fcm_tokens_tenant_id", "tenant_user_fcm_tokens", ["tenant_id"])
    op.create_index("ix_tenant_user_fcm_tokens_user_id", "tenant_user_fcm_tokens", ["user_id"])


def downgrade() -> None:
    op.drop_index("ix_tenant_user_fcm_tokens_user_id", table_name="tenant_user_fcm_tokens")
    op.drop_index("ix_tenant_user_fcm_tokens_tenant_id", table_name="tenant_user_fcm_tokens")
    op.drop_table("tenant_user_fcm_tokens")
