"""Prometheus metrics for FastAPI and domain counters."""

from __future__ import annotations

import time
from typing import TYPE_CHECKING

from prometheus_client import Counter, Histogram
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.requests import Request
from starlette.responses import Response

if TYPE_CHECKING:
    from fastapi import FastAPI

workflow_fired_total = Counter(
    "workflow_fired_total",
    "Mesh workflows executed",
    ["tenant_id", "status"],
)

device_message_rate = Counter(
    "device_message_total",
    "Device MQTT/telemetry messages ingested",
    ["tenant_id", "domain"],
)

anomaly_detected_total = Counter(
    "anomaly_detected_total",
    "Telemetry anomalies detected",
    ["tenant_id", "severity"],
)

api_request_duration_seconds = Histogram(
    "api_request_duration_seconds",
    "HTTP request latency",
    ["method", "path_template", "status_code"],
    buckets=(0.005, 0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1.0, 2.5, 5.0, 10.0),
)


def record_workflow_fired(tenant_id: str, status: str) -> None:
    workflow_fired_total.labels(tenant_id=tenant_id, status=status).inc()


def record_device_message(tenant_id: str, domain: str) -> None:
    device_message_rate.labels(tenant_id=tenant_id, domain=domain).inc()


def record_anomaly(tenant_id: str, severity: str) -> None:
    anomaly_detected_total.labels(tenant_id=tenant_id, severity=severity).inc()


class PrometheusMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        if request.url.path == "/metrics":
            return await call_next(request)
        start = time.perf_counter()
        response = await call_next(request)
        elapsed = time.perf_counter() - start
        route = request.scope.get("route")
        path_template = getattr(route, "path", request.url.path)
        api_request_duration_seconds.labels(
            method=request.method,
            path_template=str(path_template),
            status_code=str(response.status_code),
        ).observe(elapsed)
        return response


def setup_prometheus(app: FastAPI) -> None:
    """Register HTTP histogram middleware and optional instrumentator."""
    app.add_middleware(PrometheusMiddleware)
    try:
        from prometheus_fastapi_instrumentator import Instrumentator

        Instrumentator().instrument(app).expose(app, endpoint="/metrics/instrumentator", include_in_schema=False)
    except ImportError:
        pass
