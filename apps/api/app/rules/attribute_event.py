"""Attribute change events for rule hooks."""

from __future__ import annotations

from dataclasses import dataclass

from pydantic import JsonValue


@dataclass(frozen=True)
class AttributeChangeEvent:
    scope: str
    key: str
    old_value: JsonValue
    new_value: JsonValue
