"""Extend firmware releases with profile link and release notes

Revision ID: 024
Revises: 023
Create Date: 2026-10-11

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "024"
down_revision: Union[str, None] = "023"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "firmware_releases",
        sa.Column(
            "device_profile_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("device_profiles.id", ondelete="SET NULL"),
            nullable=True,
        ),
    )
    op.add_column("firmware_releases", sa.Column("release_notes", sa.Text(), nullable=True))
    op.create_index("ix_firmware_releases_device_profile_id", "firmware_releases", ["device_profile_id"])


def downgrade() -> None:
    op.drop_index("ix_firmware_releases_device_profile_id", table_name="firmware_releases")
    op.drop_column("firmware_releases", "release_notes")
    op.drop_column("firmware_releases", "device_profile_id")
