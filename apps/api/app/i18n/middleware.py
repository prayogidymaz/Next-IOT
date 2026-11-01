"""Attach resolved locale to request state (wire in main TODO)."""

from __future__ import annotations

from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.requests import Request
from starlette.responses import Response

from app.i18n.helper import locale_from_accept_language


class LocaleMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        request.state.locale = locale_from_accept_language(request.headers.get("Accept-Language"))
        return await call_next(request)
