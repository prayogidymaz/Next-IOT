"""Daily tenant usage

Revision ID: 028
Revises: 027
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "028"
down_revision: Union[str, None] = "027"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "tenant_usage_daily",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("tenant_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False),
        sa.Column("usage_date", sa.Date(), nullable=False),
        sa.Column("device_count", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("active_user_count", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("messages_count", sa.BigInteger(), nullable=False, server_default="0"),
        sa.Column("api_calls_count", sa.BigInteger(), nullable=False, server_default="0"),
        sa.Column("storage_bytes", sa.BigInteger(), nullable=False, server_default="0"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.UniqueConstraint("tenant_id", "usage_date", name="uq_tenant_usage_daily_tenant_date"),
    )
    op.create_index("ix_tenant_usage_daily_tenant_date", "tenant_usage_daily", ["tenant_id", "usage_date"])


def downgrade() -> None:
    op.drop_index("ix_tenant_usage_daily_tenant_date", table_name="tenant_usage_daily")
    op.drop_table("tenant_usage_daily")
