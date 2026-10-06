"""Partial unique indexes for active device credentials

Revision ID: 017
Revises: 016
Create Date: 2026-10-06

"""

from typing import Sequence, Union

from alembic import op

revision: str = "017"
down_revision: Union[str, None] = "016"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute("DROP INDEX IF EXISTS ix_device_credentials_client_id")
    op.execute("DROP INDEX IF EXISTS ix_device_credentials_access_token")
    op.execute(
        """
        CREATE UNIQUE INDEX ix_device_credentials_client_id_active
        ON device_credentials (client_id)
        WHERE is_active = true
        """
    )
    op.execute(
        """
        CREATE UNIQUE INDEX ix_device_credentials_access_token_active
        ON device_credentials (access_token)
        WHERE is_active = true
        """
    )


def downgrade() -> None:
    op.execute("DELETE FROM device_credentials WHERE is_active = false")
    op.execute("DROP INDEX IF EXISTS ix_device_credentials_access_token_active")
    op.execute("DROP INDEX IF EXISTS ix_device_credentials_client_id_active")
    op.create_index(
        "ix_device_credentials_client_id",
        "device_credentials",
        ["client_id"],
        unique=True,
    )
    op.create_index(
        "ix_device_credentials_access_token",
        "device_credentials",
        ["access_token"],
        unique=True,
    )
