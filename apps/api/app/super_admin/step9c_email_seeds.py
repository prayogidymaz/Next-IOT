"""Default platform email template seed data."""

from __future__ import annotations

EMAIL_TEMPLATE_SEEDS: list[dict[str, object]] = [
    {
        "code": "welcome",
        "name": "Selamat datang",
        "subject": "Selamat datang di {{ platform_name }}, {{ user_name }}!",
        "body_html": "<p>Halo {{ user_name }}, akun Anda di {{ platform_name }} sudah aktif.</p>",
        "variables": [
            {"name": "user_name", "description": "Nama penerima"},
            {"name": "platform_name", "description": "Nama platform"},
        ],
    },
    {
        "code": "verify_email",
        "name": "Verifikasi email",
        "subject": "Verifikasi email Anda — {{ platform_name }}",
        "body_html": "<p>Klik tautan: {{ verify_url }}</p>",
        "variables": [
            {"name": "verify_url", "description": "URL verifikasi"},
            {"name": "platform_name", "description": "Nama platform"},
        ],
    },
    {
        "code": "password_reset",
        "name": "Reset kata sandi",
        "subject": "Reset kata sandi {{ platform_name }}",
        "body_html": "<p>Gunakan kode: {{ reset_code }}</p>",
        "variables": [
            {"name": "reset_code", "description": "Kode reset"},
            {"name": "platform_name", "description": "Nama platform"},
        ],
    },
    {
        "code": "invoice_created",
        "name": "Invoice dibuat",
        "subject": "Invoice {{ invoice_number }}",
        "body_html": "<p>Invoice {{ invoice_number }} jatuh tempo {{ due_date }}.</p>",
        "variables": [
            {"name": "invoice_number", "description": "Nomor invoice"},
            {"name": "due_date", "description": "Jatuh tempo"},
        ],
    },
    {
        "code": "invoice_paid",
        "name": "Invoice lunas",
        "subject": "Pembayaran {{ invoice_number }}",
        "body_html": "<p>Terima kasih atas pembayaran Anda.</p>",
        "variables": [{"name": "invoice_number", "description": "Nomor invoice"}],
    },
    {
        "code": "invoice_overdue",
        "name": "Invoice terlambat",
        "subject": "Pengingat invoice {{ invoice_number }}",
        "body_html": "<p>Segera lunasi invoice {{ invoice_number }}.</p>",
        "variables": [{"name": "invoice_number", "description": "Nomor invoice"}],
    },
    {
        "code": "trial_ending",
        "name": "Trial berakhir",
        "subject": "Trial berakhir {{ trial_end_date }}",
        "body_html": "<p>Halo {{ user_name }}, upgrade sebelum {{ trial_end_date }}.</p>",
        "variables": [
            {"name": "user_name", "description": "Nama user"},
            {"name": "trial_end_date", "description": "Akhir trial"},
        ],
    },
    {
        "code": "subscription_canceled",
        "name": "Langganan dibatalkan",
        "subject": "Langganan {{ plan_name }} dibatalkan",
        "body_html": "<p>Berakhir {{ end_date }}.</p>",
        "variables": [
            {"name": "plan_name", "description": "Paket"},
            {"name": "end_date", "description": "Tanggal berakhir"},
        ],
    },
    {
        "code": "alert_notification",
        "name": "Notifikasi alarm",
        "subject": "Alarm: {{ alarm_title }}",
        "body_html": "<p>{{ alarm_message }}</p>",
        "variables": [
            {"name": "alarm_title", "description": "Judul"},
            {"name": "alarm_message", "description": "Pesan"},
        ],
    },
    {
        "code": "user_invited",
        "name": "Undangan user",
        "subject": "Undangan ke {{ tenant_name }}",
        "body_html": "<p>Buka {{ invite_url }}</p>",
        "variables": [
            {"name": "tenant_name", "description": "Tenant"},
            {"name": "invite_url", "description": "URL"},
        ],
    },
]
