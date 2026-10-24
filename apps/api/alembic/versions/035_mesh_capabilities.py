"""Mesh capability columns on device_profiles

Revision ID: 035
Revises: 034
"""

from __future__ import annotations

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "035"
down_revision: str | None = "034"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column(
        "device_profiles",
        sa.Column("capabilities", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
    )
    op.add_column(
        "device_profiles",
        sa.Column("geo_location", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
    )
    op.add_column(
        "device_profiles",
        sa.Column("physical_zone", sa.String(length=128), nullable=True),
    )
    op.add_column(
        "device_profiles",
        sa.Column("network_adjacency", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
    )


def downgrade() -> None:
    op.drop_column("device_profiles", "network_adjacency")
    op.drop_column("device_profiles", "physical_zone")
    op.drop_column("device_profiles", "geo_location")
    op.drop_column("device_profiles", "capabilities")
