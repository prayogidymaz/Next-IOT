"""JSON-safe types for API payloads (no typing.Any)."""

from pydantic import JsonValue

JsonObject = dict[str, JsonValue]
JsonArray = list[JsonValue]

__all__ = ["JsonArray", "JsonObject", "JsonValue"]
