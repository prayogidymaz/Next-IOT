"""ML analytics tables (yield, anomaly, optimization)

Revision ID: 041
Revises: 040
"""

from __future__ import annotations

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "041"
down_revision: str | None = "040"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "yield_forecasts",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("plot_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("tenant_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("forecast_date", sa.Date(), nullable=False),
        sa.Column("estimated_kg", sa.Numeric(12, 3), nullable=False),
        sa.Column("ci_low", sa.Numeric(12, 3), nullable=False),
        sa.Column("ci_high", sa.Numeric(12, 3), nullable=False),
        sa.Column("model_version", sa.String(length=32), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["tenant_id"], ["tenants.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_yield_forecasts_plot_id", "yield_forecasts", ["plot_id"])
    op.create_index("ix_yield_forecasts_tenant_id", "yield_forecasts", ["tenant_id"])

    op.create_table(
        "anomaly_events",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("tenant_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("device_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("detected_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("metric", sa.String(length=64), nullable=False),
        sa.Column("value", sa.Numeric(14, 4), nullable=False),
        sa.Column("expected_min", sa.Numeric(14, 4), nullable=False),
        sa.Column("expected_max", sa.Numeric(14, 4), nullable=False),
        sa.Column("severity", sa.String(length=16), nullable=False),
        sa.Column("acknowledged", sa.Boolean(), nullable=False, server_default=sa.text("false")),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["device_id"], ["devices.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["tenant_id"], ["tenants.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_anomaly_events_device_id", "anomaly_events", ["device_id"])
    op.create_index("ix_anomaly_events_tenant_id", "anomaly_events", ["tenant_id"])

    op.create_table(
        "optimization_reports",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("tenant_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("period_start", sa.DateTime(timezone=True), nullable=False),
        sa.Column("period_end", sa.DateTime(timezone=True), nullable=False),
        sa.Column("recommendations_json", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column("total_saving_idr", sa.Numeric(16, 2), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["tenant_id"], ["tenants.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_optimization_reports_tenant_id", "optimization_reports", ["tenant_id"])


def downgrade() -> None:
    op.drop_index("ix_optimization_reports_tenant_id", table_name="optimization_reports")
    op.drop_table("optimization_reports")
    op.drop_index("ix_anomaly_events_tenant_id", table_name="anomaly_events")
    op.drop_index("ix_anomaly_events_device_id", table_name="anomaly_events")
    op.drop_table("anomaly_events")
    op.drop_index("ix_yield_forecasts_tenant_id", table_name="yield_forecasts")
    op.drop_index("ix_yield_forecasts_plot_id", table_name="yield_forecasts")
    op.drop_table("yield_forecasts")
