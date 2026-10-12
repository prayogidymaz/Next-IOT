"""Step 9C: email templates, support, partners, backups, impersonation sessions

Revision ID: 032
Revises: 031
"""

from __future__ import annotations

import uuid
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "032"
down_revision: Union[str, None] = "031"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

_TEMPLATE_SEEDS: list[dict[str, object]] = [
    {
        "code": "welcome",
        "name": "Selamat datang",
        "subject": "Selamat datang di {{ platform_name }}, {{ user_name }}!",
        "body_html": "<p>Halo {{ user_name }}, akun Anda di {{ platform_name }} sudah aktif.</p>",
        "variables": [{"name": "user_name", "description": "Nama penerima"}, {"name": "platform_name", "description": "Nama platform"}],
    },
    {
        "code": "verify_email",
        "name": "Verifikasi email",
        "subject": "Verifikasi email Anda — {{ platform_name }}",
        "body_html": "<p>Klik tautan: {{ verify_url }}</p>",
        "variables": [{"name": "verify_url", "description": "URL verifikasi"}, {"name": "platform_name", "description": "Nama platform"}],
    },
    {
        "code": "password_reset",
        "name": "Reset kata sandi",
        "subject": "Reset kata sandi {{ platform_name }}",
        "body_html": "<p>Gunakan kode: {{ reset_code }}</p>",
        "variables": [{"name": "reset_code", "description": "Kode reset"}, {"name": "platform_name", "description": "Nama platform"}],
    },
    {
        "code": "invoice_created",
        "name": "Invoice dibuat",
        "subject": "Invoice {{ invoice_number }} — {{ total_idr }} IDR",
        "body_html": "<p>Invoice {{ invoice_number }} jatuh tempo {{ due_date }}.</p>",
        "variables": [
            {"name": "invoice_number", "description": "Nomor invoice"},
            {"name": "total_idr", "description": "Total IDR"},
            {"name": "due_date", "description": "Jatuh tempo"},
        ],
    },
    {
        "code": "invoice_paid",
        "name": "Invoice lunas",
        "subject": "Pembayaran diterima — {{ invoice_number }}",
        "body_html": "<p>Terima kasih, pembayaran {{ total_idr }} IDR telah kami terima.</p>",
        "variables": [{"name": "invoice_number", "description": "Nomor invoice"}, {"name": "total_idr", "description": "Total IDR"}],
    },
    {
        "code": "invoice_overdue",
        "name": "Invoice terlambat",
        "subject": "Pengingat: invoice {{ invoice_number }} terlambat",
        "body_html": "<p>Segera lunasi invoice {{ invoice_number }} sebesar {{ total_idr }} IDR.</p>",
        "variables": [{"name": "invoice_number", "description": "Nomor invoice"}, {"name": "total_idr", "description": "Total IDR"}],
    },
    {
        "code": "trial_ending",
        "name": "Trial berakhir",
        "subject": "Trial Anda berakhir {{ trial_end_date }}",
        "body_html": "<p>Halo {{ user_name }}, upgrade paket sebelum {{ trial_end_date }}.</p>",
        "variables": [{"name": "user_name", "description": "Nama user"}, {"name": "trial_end_date", "description": "Tanggal akhir trial"}],
    },
    {
        "code": "subscription_canceled",
        "name": "Langganan dibatalkan",
        "subject": "Langganan {{ plan_name }} dibatalkan",
        "body_html": "<p>Langganan {{ plan_name }} berakhir pada {{ end_date }}.</p>",
        "variables": [{"name": "plan_name", "description": "Nama paket"}, {"name": "end_date", "description": "Tanggal berakhir"}],
    },
    {
        "code": "alert_notification",
        "name": "Notifikasi alarm",
        "subject": "Alarm: {{ alarm_title }}",
        "body_html": "<p>{{ alarm_message }} — perangkat {{ device_name }}</p>",
        "variables": [
            {"name": "alarm_title", "description": "Judul alarm"},
            {"name": "alarm_message", "description": "Pesan"},
            {"name": "device_name", "description": "Nama perangkat"},
        ],
    },
    {
        "code": "user_invited",
        "name": "Undangan user",
        "subject": "Anda diundang ke {{ tenant_name }}",
        "body_html": "<p>{{ inviter_name }} mengundang Anda. Buka {{ invite_url }}</p>",
        "variables": [
            {"name": "tenant_name", "description": "Nama tenant"},
            {"name": "inviter_name", "description": "Pengundang"},
            {"name": "invite_url", "description": "URL undangan"},
        ],
    },
]


def upgrade() -> None:
    op.create_table(
        "platform_email_templates",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("code", sa.String(64), nullable=False, unique=True),
        sa.Column("name", sa.String(200), nullable=False),
        sa.Column("subject", sa.String(500), nullable=False),
        sa.Column("body_html", sa.Text(), nullable=False),
        sa.Column("body_text", sa.Text(), nullable=True),
        sa.Column("variables", postgresql.JSONB(), nullable=False, server_default="[]"),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.text("true")),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_by", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="SET NULL"), nullable=True),
    )

    op.create_table(
        "support_tickets",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("tenant_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("tenants.id", ondelete="SET NULL"), nullable=True),
        sa.Column("created_by", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="SET NULL"), nullable=True),
        sa.Column("subject", sa.String(300), nullable=False),
        sa.Column("description", sa.Text(), nullable=False),
        sa.Column("category", sa.String(32), nullable=False, server_default="other"),
        sa.Column("priority", sa.String(16), nullable=False, server_default="normal"),
        sa.Column("status", sa.String(32), nullable=False, server_default="open"),
        sa.Column("assigned_to", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="SET NULL"), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("resolved_at", sa.DateTime(timezone=True), nullable=True),
    )
    op.create_index("ix_support_tickets_status", "support_tickets", ["status"])

    op.create_table(
        "support_ticket_messages",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("ticket_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("support_tickets.id", ondelete="CASCADE"), nullable=False),
        sa.Column("author_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="SET NULL"), nullable=True),
        sa.Column("is_internal", sa.Boolean(), nullable=False, server_default=sa.text("false")),
        sa.Column("body", sa.Text(), nullable=False),
        sa.Column("attachments", postgresql.JSONB(), nullable=False, server_default="[]"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )

    op.create_table(
        "partners",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("name", sa.String(200), nullable=False),
        sa.Column("contact_email", sa.String(320), nullable=False, server_default=""),
        sa.Column("contact_phone", sa.String(64), nullable=False, server_default=""),
        sa.Column("contact_person", sa.String(200), nullable=False, server_default=""),
        sa.Column("company_name", sa.String(200), nullable=False, server_default=""),
        sa.Column("address", sa.Text(), nullable=False, server_default=""),
        sa.Column("tax_id", sa.String(64), nullable=False, server_default=""),
        sa.Column("tier", sa.String(16), nullable=False, server_default="silver"),
        sa.Column("commission_percent", sa.Numeric(5, 2), nullable=False, server_default="10.00"),
        sa.Column("status", sa.String(16), nullable=False, server_default="pending"),
        sa.Column("referral_code", sa.String(32), nullable=False, unique=True),
        sa.Column("notes", sa.Text(), nullable=False, server_default=""),
        sa.Column("joined_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )

    op.create_table(
        "partner_referrals",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("partner_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("partners.id", ondelete="CASCADE"), nullable=False),
        sa.Column("tenant_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False),
        sa.Column("referred_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("first_payment_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("total_revenue_idr", sa.BigInteger(), nullable=False, server_default="0"),
        sa.Column("total_commission_idr", sa.BigInteger(), nullable=False, server_default="0"),
        sa.UniqueConstraint("partner_id", "tenant_id", name="uq_partner_referral_tenant"),
    )

    op.create_table(
        "partner_commissions",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("partner_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("partners.id", ondelete="CASCADE"), nullable=False),
        sa.Column("period_month", sa.Date(), nullable=False),
        sa.Column("total_commission_idr", sa.BigInteger(), nullable=False, server_default="0"),
        sa.Column("status", sa.String(16), nullable=False, server_default="pending"),
        sa.Column("paid_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("invoice_url", sa.Text(), nullable=True),
        sa.UniqueConstraint("partner_id", "period_month", name="uq_partner_commission_period"),
    )

    op.create_table(
        "platform_backups",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("backup_type", sa.String(32), nullable=False),
        sa.Column("size_bytes", sa.BigInteger(), nullable=False, server_default="0"),
        sa.Column("storage_path", sa.String(512), nullable=False, server_default=""),
        sa.Column("started_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("status", sa.String(16), nullable=False, server_default="running"),
        sa.Column("error_message", sa.Text(), nullable=True),
        sa.Column("triggered_by", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="SET NULL"), nullable=True),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=True),
    )

    op.create_table(
        "impersonation_sessions",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("super_admin_user_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="SET NULL"), nullable=True),
        sa.Column("tenant_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("tenants.id", ondelete="SET NULL"), nullable=True),
        sa.Column("started_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("ended_at", sa.DateTime(timezone=True), nullable=True),
    )

    op.create_table(
        "impersonation_session_actions",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("session_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("impersonation_sessions.id", ondelete="CASCADE"), nullable=False),
        sa.Column("action", sa.String(128), nullable=False),
        sa.Column("resource", sa.String(512), nullable=False, server_default=""),
        sa.Column("detail", postgresql.JSONB(), nullable=False, server_default="{}"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )

    op.add_column(
        "tenants",
        sa.Column("referred_by_partner_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("partners.id", ondelete="SET NULL"), nullable=True),
    )

    templates = sa.table(
        "platform_email_templates",
        sa.column("id", postgresql.UUID(as_uuid=True)),
        sa.column("code", sa.String),
        sa.column("name", sa.String),
        sa.column("subject", sa.String),
        sa.column("body_html", sa.Text),
        sa.column("body_text", sa.Text),
        sa.column("variables", postgresql.JSONB),
        sa.column("is_active", sa.Boolean),
    )
    op.bulk_insert(
        templates,
        [
            {
                "id": uuid.uuid4(),
                "code": row["code"],
                "name": row["name"],
                "subject": row["subject"],
                "body_html": row["body_html"],
                "body_text": None,
                "variables": row["variables"],
                "is_active": True,
            }
            for row in _TEMPLATE_SEEDS
        ],
    )


def downgrade() -> None:
    op.drop_column("tenants", "referred_by_partner_id")
    op.drop_table("impersonation_session_actions")
    op.drop_table("impersonation_sessions")
    op.drop_table("platform_backups")
    op.drop_table("partner_commissions")
    op.drop_table("partner_referrals")
    op.drop_table("partners")
    op.drop_table("support_ticket_messages")
    op.drop_table("support_tickets")
    op.drop_table("platform_email_templates")
