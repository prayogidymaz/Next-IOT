"""MQTT device credentials and QR claim tokens

Revision ID: 016
Revises: 015
Create Date: 2026-10-06

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "016"
down_revision: Union[str, None] = "015"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

credential_type_enum = postgresql.ENUM(
    "access_token",
    "mtls_cert",
    "basic_auth",
    name="credential_type",
    create_type=False,
)


def upgrade() -> None:
    op.execute('CREATE EXTENSION IF NOT EXISTS "pgcrypto"')

    op.execute(
        """
        DO $$ BEGIN
            CREATE TYPE credential_type AS ENUM ('access_token', 'mtls_cert', 'basic_auth');
        EXCEPTION
            WHEN duplicate_object THEN NULL;
        END $$
        """
    )

    op.add_column(
        "device_credentials",
        sa.Column("tenant_id", postgresql.UUID(as_uuid=True), nullable=True),
    )
    op.execute(
        """
        UPDATE device_credentials dc
        SET tenant_id = d.tenant_id
        FROM devices d
        WHERE dc.device_id = d.id
        """
    )
    op.alter_column("device_credentials", "tenant_id", nullable=False)
    op.create_foreign_key(
        "fk_device_credentials_tenant_id",
        "device_credentials",
        "tenants",
        ["tenant_id"],
        ["id"],
        ondelete="CASCADE",
    )
    op.create_index("ix_device_credentials_tenant_id", "device_credentials", ["tenant_id"])

    op.add_column(
        "device_credentials",
        sa.Column(
            "credential_type",
            credential_type_enum,
            nullable=False,
            server_default="basic_auth",
        ),
    )
    op.add_column(
        "device_credentials",
        sa.Column("access_token", sa.String(64), nullable=True),
    )
    op.execute(
        """
        UPDATE device_credentials
        SET access_token = replace(replace(encode(gen_random_bytes(27), 'base64'), '+', '-'), '/', '_')
        WHERE access_token IS NULL
        """
    )
    op.alter_column("device_credentials", "access_token", nullable=False)
    op.create_index("ix_device_credentials_access_token", "device_credentials", ["access_token"], unique=True)

    op.add_column(
        "device_credentials",
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.text("true")),
    )
    op.execute(
        """
        UPDATE device_credentials
        SET is_active = (revoked_at IS NULL)
        """
    )

    op.add_column(
        "device_credentials",
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=True),
    )
    op.execute("UPDATE device_credentials SET created_at = issued_at WHERE created_at IS NULL")
    op.alter_column("device_credentials", "created_at", nullable=False)

    op.add_column(
        "device_credentials",
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.add_column("device_credentials", sa.Column("last_connected_at", sa.DateTime(timezone=True), nullable=True))
    op.add_column("device_credentials", sa.Column("rotated_at", sa.DateTime(timezone=True), nullable=True))

    op.alter_column(
        "device_credentials",
        "client_id",
        existing_type=sa.String(100),
        type_=sa.String(128),
        existing_nullable=False,
    )
    op.alter_column("device_credentials", "secret_hash", existing_type=sa.String(255), nullable=True)

    op.drop_column("device_credentials", "revoked_at")
    op.drop_column("device_credentials", "issued_at")

    op.create_index(
        "ix_device_credentials_tenant_device",
        "device_credentials",
        ["tenant_id", "device_id"],
    )
    op.execute(
        """
        CREATE UNIQUE INDEX uq_device_credentials_one_active_per_device
        ON device_credentials (device_id)
        WHERE is_active = true
        """
    )

    op.create_table(
        "device_claim_tokens",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "tenant_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("tenants.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("claim_token", sa.String(32), nullable=False),
        sa.Column("device_name", sa.String(255), nullable=False),
        sa.Column("device_type", sa.String(100), nullable=False),
        sa.Column("device_category", sa.String(64), nullable=False),
        sa.Column(
            "profile_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("device_profiles.id", ondelete="SET NULL"),
            nullable=True,
        ),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("claimed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column(
            "claimed_device_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("devices.id", ondelete="SET NULL"),
            nullable=True,
        ),
        sa.Column(
            "created_by_user_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("users.id", ondelete="SET NULL"),
            nullable=True,
        ),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index("ix_device_claim_tokens_claim_token", "device_claim_tokens", ["claim_token"], unique=True)
    op.create_index("ix_device_claim_tokens_tenant_id", "device_claim_tokens", ["tenant_id"])


def downgrade() -> None:
    op.drop_index("ix_device_claim_tokens_tenant_id", table_name="device_claim_tokens")
    op.drop_index("ix_device_claim_tokens_claim_token", table_name="device_claim_tokens")
    op.drop_table("device_claim_tokens")

    op.execute("DROP INDEX IF EXISTS uq_device_credentials_one_active_per_device")
    op.drop_index("ix_device_credentials_tenant_device", table_name="device_credentials")
    op.drop_index("ix_device_credentials_access_token", table_name="device_credentials")
    op.drop_index("ix_device_credentials_tenant_id", table_name="device_credentials")
    op.drop_constraint("fk_device_credentials_tenant_id", "device_credentials", type_="foreignkey")

    op.add_column("device_credentials", sa.Column("issued_at", sa.DateTime(timezone=True), nullable=True))
    op.execute("UPDATE device_credentials SET issued_at = created_at")
    op.alter_column("device_credentials", "issued_at", nullable=False, server_default=sa.func.now())

    op.add_column("device_credentials", sa.Column("revoked_at", sa.DateTime(timezone=True), nullable=True))
    op.execute("UPDATE device_credentials SET revoked_at = now() WHERE is_active = false")

    op.drop_column("device_credentials", "rotated_at")
    op.drop_column("device_credentials", "last_connected_at")
    op.drop_column("device_credentials", "updated_at")
    op.drop_column("device_credentials", "created_at")
    op.drop_column("device_credentials", "is_active")
    op.drop_column("device_credentials", "access_token")
    op.drop_column("device_credentials", "credential_type")
    op.drop_column("device_credentials", "tenant_id")

    op.alter_column(
        "device_credentials",
        "client_id",
        existing_type=sa.String(128),
        type_=sa.String(100),
        existing_nullable=False,
    )
    op.alter_column("device_credentials", "secret_hash", existing_type=sa.String(255), nullable=False)

    op.execute("DROP TYPE credential_type")
