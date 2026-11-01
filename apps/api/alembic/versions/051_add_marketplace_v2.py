"""Marketplace v2 seller tiers and paid templates

Revision ID: 051
Revises: 050
"""

from __future__ import annotations

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "051"
down_revision: str | None = "050"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column("workflow_templates", sa.Column("price_idr", sa.Integer(), nullable=False, server_default="0"))
    op.add_column("workflow_templates", sa.Column("stripe_product_id", sa.String(length=128), nullable=True))
    op.add_column("workflow_templates", sa.Column("author_user_id", postgresql.UUID(as_uuid=True), nullable=True))
    op.create_foreign_key(
        "fk_workflow_templates_author_user",
        "workflow_templates",
        "users",
        ["author_user_id"],
        ["id"],
        ondelete="SET NULL",
    )

    op.create_table(
        "marketplace_sellers",
        sa.Column("user_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("tenant_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("tier", sa.String(length=16), nullable=False, server_default="bronze"),
        sa.Column("commission_rate_percent", sa.Numeric(5, 2), nullable=False, server_default="15"),
        sa.Column("lifetime_sales_idr", sa.BigInteger(), nullable=False, server_default="0"),
        sa.Column("verified_badge", sa.Boolean(), nullable=False, server_default=sa.text("false")),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["tenant_id"], ["tenants.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("user_id"),
    )

    op.create_table(
        "marketplace_payouts",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("seller_user_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("period_month", sa.String(length=7), nullable=False),
        sa.Column("gross_sales_idr", sa.BigInteger(), nullable=False, server_default="0"),
        sa.Column("commission_idr", sa.BigInteger(), nullable=False, server_default="0"),
        sa.Column("status", sa.String(length=32), nullable=False, server_default="pending"),
        sa.Column("paid_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("transaction_ref", sa.String(length=128), nullable=True),
        sa.ForeignKeyConstraint(["seller_user_id"], ["marketplace_sellers.user_id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_marketplace_payouts_seller", "marketplace_payouts", ["seller_user_id"])

    op.create_table(
        "marketplace_template_purchases",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("template_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("buyer_tenant_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("amount_idr", sa.Integer(), nullable=False),
        sa.Column("payment_provider", sa.String(length=32), nullable=False, server_default="midtrans"),
        sa.Column("payment_ref", sa.String(length=128), nullable=True),
        sa.Column("status", sa.String(length=32), nullable=False, server_default="paid"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["buyer_tenant_id"], ["tenants.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["template_id"], ["workflow_templates.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )


def downgrade() -> None:
    op.drop_table("marketplace_template_purchases")
    op.drop_index("ix_marketplace_payouts_seller", table_name="marketplace_payouts")
    op.drop_table("marketplace_payouts")
    op.drop_table("marketplace_sellers")
    op.drop_constraint("fk_workflow_templates_author_user", "workflow_templates", type_="foreignkey")
    op.drop_column("workflow_templates", "author_user_id")
    op.drop_column("workflow_templates", "stripe_product_id")
    op.drop_column("workflow_templates", "price_idr")
