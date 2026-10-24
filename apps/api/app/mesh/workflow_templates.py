"""Render {{dotted.path}} templates for mesh workflows."""

from __future__ import annotations

import re
from collections.abc import Mapping

from pydantic import JsonValue

from app.types.json_types import JsonObject

_TEMPLATE_PATTERN = re.compile(r"\{\{\s*([^}]+?)\s*\}}")


def _resolve_path(root: Mapping[str, object], path: str) -> JsonValue | None:
    current: object = root
    for part in path.split("."):
        if not isinstance(current, Mapping):
            return None
        current = current.get(part)
    if isinstance(current, str | int | float | bool) or current is None:
        return current
    if isinstance(current, list):
        return current
    if isinstance(current, dict):
        return current
    return str(current)


def render_template_string(value: str, context: Mapping[str, object]) -> str:
    def replacer(match: re.Match[str]) -> str:
        path = match.group(1).strip()
        resolved = _resolve_path(context, path)
        if resolved is None:
            return ""
        return str(resolved)

    return _TEMPLATE_PATTERN.sub(replacer, value)


def render_json_value(value: JsonValue, context: Mapping[str, object]) -> JsonValue:
    if isinstance(value, str):
        if "{{" in value and "}}" in value:
            return render_template_string(value, context)
        return value
    if isinstance(value, list):
        return [render_json_value(item, context) for item in value]
    if isinstance(value, dict):
        out: JsonObject = {}
        for key, item in value.items():
            out[key] = render_json_value(item, context)
        return out
    return value


def render_json_object(value: JsonObject, context: Mapping[str, object]) -> JsonObject:
    rendered = render_json_value(value, context)
    if isinstance(rendered, dict):
        return rendered
    return {}
