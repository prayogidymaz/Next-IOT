"""Sustainability ESG carbon and water tables

Revision ID: 049
Revises: 048
"""

from __future__ import annotations

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "049"
down_revision: str | None = "048"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "carbon_entries",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("tenant_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("site_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("source_type", sa.String(length=64), nullable=False),
        sa.Column("amount", sa.Numeric(18, 6), nullable=False),
        sa.Column("co2_equivalent_kg", sa.Numeric(18, 6), nullable=False),
        sa.Column("recorded_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("auto_calculated", sa.Boolean(), nullable=False, server_default=sa.text("false")),
        sa.ForeignKeyConstraint(["site_id"], ["sites.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["tenant_id"], ["tenants.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_carbon_entries_tenant_recorded", "carbon_entries", ["tenant_id", "recorded_at"])

    op.create_table(
        "water_usage",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("tenant_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("site_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("plot_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("liters_used", sa.Numeric(18, 3), nullable=False),
        sa.Column("source", sa.String(length=32), nullable=False),
        sa.Column("recorded_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["plot_id"], ["plots.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["site_id"], ["sites.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["tenant_id"], ["tenants.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_water_usage_tenant_recorded", "water_usage", ["tenant_id", "recorded_at"])

    op.create_table(
        "esg_scorecards",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("tenant_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("period_month", sa.String(length=7), nullable=False),
        sa.Column("environmental_score", sa.Numeric(5, 2), nullable=False),
        sa.Column("social_score", sa.Numeric(5, 2), nullable=False),
        sa.Column("governance_score", sa.Numeric(5, 2), nullable=False),
        sa.Column("overall_grade", sa.String(length=2), nullable=False),
        sa.Column("generated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("report_pdf_url", sa.String(length=512), nullable=True),
        sa.ForeignKeyConstraint(["tenant_id"], ["tenants.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("tenant_id", "period_month", name="uq_esg_tenant_month"),
    )


def downgrade() -> None:
    op.drop_table("esg_scorecards")
    op.drop_index("ix_water_usage_tenant_recorded", table_name="water_usage")
    op.drop_table("water_usage")
    op.drop_index("ix_carbon_entries_tenant_recorded", table_name="carbon_entries")
    op.drop_table("carbon_entries")
