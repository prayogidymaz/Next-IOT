"""Locale helpers."""

from __future__ import annotations

from app.i18n.translations import ALERT_MESSAGES, API_ERROR_MESSAGES, EMAIL_TEMPLATES
from app.i18n.types import DEFAULT_LOCALE, LocaleCode

CATALOGS: dict[str, dict[str, dict[LocaleCode, str]]] = {
    "alert": ALERT_MESSAGES,
    "email": EMAIL_TEMPLATES,
    "api_error": API_ERROR_MESSAGES,
}


def normalize_locale(raw: str | None) -> LocaleCode:
    if not raw:
        return DEFAULT_LOCALE
    value = raw.lower().replace("_", "-")
    if value.startswith("zh"):
        return "zh-CN"
    if value.startswith("en"):
        return "en"
    return "id"


def translate(key: str, locale: LocaleCode, category: str = "api_error") -> str:
    catalog = CATALOGS.get(category, API_ERROR_MESSAGES)
    entry = catalog.get(key)
    if entry is None:
        return key
    return entry.get(locale, entry.get("en", key))


def locale_from_accept_language(header: str | None) -> LocaleCode:
    if not header:
        return DEFAULT_LOCALE
    first = header.split(",")[0].split(";")[0].strip()
    return normalize_locale(first)
