"""Static translation catalog."""

from __future__ import annotations

from app.i18n.types import LocaleCode

ALERT_MESSAGES: dict[str, dict[LocaleCode, str]] = {
    "alarm.created": {
        "id": "Alarm baru dibuat",
        "en": "New alarm created",
        "zh-CN": "新告警已创建",
    },
    "device.offline": {
        "id": "Perangkat offline",
        "en": "Device offline",
        "zh-CN": "设备离线",
    },
}

EMAIL_TEMPLATES: dict[str, dict[LocaleCode, str]] = {
    "invite.subject": {
        "id": "Undangan bergabung ke Next-IoT",
        "en": "Invitation to join Next-IoT",
        "zh-CN": "加入 Next-IoT 的邀请",
    },
}

API_ERROR_MESSAGES: dict[str, dict[LocaleCode, str]] = {
    "not_found": {
        "id": "Tidak ditemukan",
        "en": "Not found",
        "zh-CN": "未找到",
    },
    "forbidden": {
        "id": "Akses ditolak",
        "en": "Forbidden",
        "zh-CN": "禁止访问",
    },
}
