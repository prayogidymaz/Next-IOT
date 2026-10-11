"""Super admin action audit log

Revision ID: 030
Revises: 029
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "030"
down_revision: Union[str, None] = "029"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "super_admin_actions",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("actor_user_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="SET NULL"), nullable=True),
        sa.Column("action", sa.String(64), nullable=False),
        sa.Column("target_tenant_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("tenants.id", ondelete="SET NULL"), nullable=True),
        sa.Column("detail", postgresql.JSONB(), nullable=False, server_default=sa.text("'{}'::jsonb")),
        sa.Column("note", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index("ix_super_admin_actions_actor_user_id", "super_admin_actions", ["actor_user_id"])
    op.create_index("ix_super_admin_actions_action", "super_admin_actions", ["action"])
    op.create_index("ix_super_admin_actions_target_tenant_id", "super_admin_actions", ["target_tenant_id"])


def downgrade() -> None:
    op.drop_index("ix_super_admin_actions_target_tenant_id", table_name="super_admin_actions")
    op.drop_index("ix_super_admin_actions_action", table_name="super_admin_actions")
    op.drop_index("ix_super_admin_actions_actor_user_id", table_name="super_admin_actions")
    op.drop_table("super_admin_actions")
