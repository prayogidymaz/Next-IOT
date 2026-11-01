"""Enhance OpenAPI schema for developer portal."""

from __future__ import annotations

from fastapi import FastAPI
from fastapi.openapi.utils import get_openapi


def attach_custom_openapi(app: FastAPI) -> None:
    def custom_openapi() -> dict[str, object]:
        if app.openapi_schema is not None:
            return app.openapi_schema
        schema = get_openapi(
            title=app.title,
            version=app.version,
            description=(
                "Next-IOT Platform REST API.\n\n"
                "## Authentication\n"
                "Use `Authorization: Bearer <access_token>` from `/auth/login`.\n\n"
                "## Tenant scope\n"
                "Most routes are scoped to the authenticated user's tenant."
            ),
            routes=app.routes,
        )
        schema["tags"] = [
            {"name": "sites", "description": "Multi-site enterprise hierarchy (HQ → Site → Plot)."},
            {"name": "sustainability", "description": "Carbon, water, and ESG scorecards."},
            {"name": "webhooks", "description": "Outbound event webhooks with HMAC signatures."},
            {"name": "workflow-marketplace", "description": "Publish and download workflow templates."},
        ]
        paths = schema.get("paths")
        if isinstance(paths, dict):
            for path_item in paths.values():
                if not isinstance(path_item, dict):
                    continue
                for operation in path_item.values():
                    if not isinstance(operation, dict):
                        continue
                    responses = operation.get("responses")
                    if isinstance(responses, dict) and "401" not in responses:
                        responses["401"] = {"description": "Missing or invalid bearer token"}
                    if isinstance(responses, dict) and "403" not in responses:
                        responses["403"] = {"description": "Insufficient role or tenant scope"}
        app.openapi_schema = schema
        return schema

    app.openapi = custom_openapi
