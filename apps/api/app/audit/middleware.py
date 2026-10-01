"""HTTP middleware — records auditable API mutations after response."""

from __future__ import annotations

import logging
import re

from app.audit.actions import AuditAction
from app.audit.service import client_ip, record_audit_event
from app.auth.context import CurrentUser
from app.database import async_session
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response

logger = logging.getLogger(__name__)

_DEVICE_CMD = re.compile(r"^/api/v1/devices/([0-9a-f-]{36})/commands$")
_RULE_ID = re.compile(r"^/api/v1/rules(?:/([0-9a-f-]{36}))?$")
_TENANT_MEMBERS = re.compile(r"^/api/v1/tenants/([0-9a-f-]{36})/members$")


def _status_label(code: int) -> str:
    return "success" if 200 <= code < 400 else "failure"


def _resolve_action(method: str, path: str) -> tuple[str | None, str]:
    if method == "POST" and path == "/api/v1/devices":
        return AuditAction.DEVICE_REGISTER, "device"
    if method == "POST" and _DEVICE_CMD.match(path):
        match = _DEVICE_CMD.match(path)
        return AuditAction.DEVICE_COMMAND, f"device:{match.group(1)}"
    if method == "POST" and path == "/api/v1/ota/releases":
        return AuditAction.OTA_UPLOAD, "firmware_release"
    if path.startswith("/api/v1/rules") and method in {"POST", "PATCH", "DELETE"}:
        match = _RULE_ID.match(path)
        target = f"rule:{match.group(1)}" if match and match.group(1) else "rule"
        return AuditAction.RULE_MUTATION, target
    if method == "POST" and path == "/api/v1/tenants":
        return AuditAction.TENANT_UPDATE, "tenant:create"
    if method == "POST" and _TENANT_MEMBERS.match(path):
        match = _TENANT_MEMBERS.match(path)
        return AuditAction.TENANT_UPDATE, f"tenant:{match.group(1)}/member"
    return None, ""


class AuditLoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next) -> Response:
        response = await call_next(request)
        action, resource = _resolve_action(request.method.upper(), request.url.path)
        if not action:
            return response

        user: CurrentUser | None = getattr(request.state, "current_user", None)
        if user is None:
            return response

        try:
            async with async_session() as db:
                await record_audit_event(
                    db,
                    action=action,
                    actor_id=user.user_id,
                    actor_email=user.email,
                    tenant_id=user.tenant_id,
                    resource_target=resource,
                    ip_address=client_ip(request),
                    status=_status_label(response.status_code),
                )
        except Exception:
            logger.exception("Audit middleware failed for %s %s", request.method, request.url.path)
        return response
