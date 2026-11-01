"""Shared i18n types (no imports from other app.i18n modules)."""

from typing import Literal

LocaleCode = Literal["id", "en", "zh-CN"]
DEFAULT_LOCALE: LocaleCode = "id"
