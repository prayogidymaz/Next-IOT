"""Idempotent EMQX Dashboard API setup for telemetry HTTP forwarding."""

from __future__ import annotations

import asyncio
import logging
from typing import TypedDict
from urllib.parse import urlparse, urlunparse

import httpx
from app.config import settings

logger = logging.getLogger(__name__)

CONNECTOR_NAME = "api_mqtt_ingest"
ACTION_NAME = "forward_telemetry"
RULE_NAME = "rule_forward_telemetry"
RULE_SQL = 'SELECT * FROM "tenants/+/devices/+/telemetry"'
HTTP_ACTION_REF = f"http:{ACTION_NAME}"
# EMQX rule action template — only fields accepted by MqttTelemetryIngestRequest (no ${.} whole event).
ACTION_INGEST_BODY_TEMPLATE = (
    '{"topic":"${topic}","payload":${payload},'
    '"clientid":"${clientid}","username":"${username}"}'
)

_AUTH_FAILURE_MESSAGE = (
    "EMQX API auth failed. Check EMQX_API_KEY env match "
    "EMQX_API_KEY__BOOTSTRAP_FILE di emqx service"
)


class _SslEnableOnly(TypedDict):
    enable: bool


class _HttpConnectorBody(TypedDict):
    type: str
    name: str
    enable: bool
    url: str
    connect_timeout: str
    pool_type: str
    pool_size: int
    enable_pipelining: int
    ssl: _SslEnableOnly


class _HttpActionParameters(TypedDict):
    method: str
    path: str
    body: str
    headers: dict[str, str]
    max_retries: int


class _HttpActionBody(TypedDict):
    type: str
    name: str
    connector: str
    parameters: _HttpActionParameters


class _HttpActionPutBody(TypedDict):
    connector: str
    parameters: _HttpActionParameters


class _RuleBody(TypedDict):
    name: str
    enable: bool
    sql: str
    actions: list[str]


def validate_emqx_api_credentials() -> None:
    if not settings.emqx_api_key.strip() or not settings.emqx_api_secret.strip():
        raise ValueError("EMQX_API_KEY and EMQX_API_SECRET are required")


def _auth() -> httpx.BasicAuth:
    return httpx.BasicAuth(settings.emqx_api_key, settings.emqx_api_secret)


def _api_key_log_prefix() -> str:
    key = settings.emqx_api_key.strip()
    if len(key) <= 8:
        return key
    return f"{key[:8]}…"


def _dashboard_url(path: str) -> str:
    base = settings.emqx_dashboard_url.rstrip("/")
    return f"{base}{path}"


def _ingest_webhook_parts() -> tuple[str, str]:
    """Split ingest URL into HTTP connector base URL and action path (EMQX 5.8)."""
    parsed = urlparse(settings.emqx_ingest_webhook_url.strip())
    if not parsed.scheme or not parsed.netloc:
        raise ValueError(f"Invalid EMQX ingest webhook URL: {settings.emqx_ingest_webhook_url}")
    base_url = urlunparse((parsed.scheme, parsed.netloc, "", "", "", ""))
    path = parsed.path if parsed.path else "/"
    return base_url, path


def _items_from_list_response(payload: object) -> list[object]:
    if isinstance(payload, list):
        return payload
    if isinstance(payload, dict):
        data = payload.get("data")
        if isinstance(data, list):
            return data
    return []


def _find_resource_named(items: list[object], name: str) -> dict[str, object] | None:
    for entry in items:
        if isinstance(entry, dict):
            entry_name = entry.get("name")
            if isinstance(entry_name, str) and entry_name == name:
                return entry
            entry_id = entry.get("id")
            if isinstance(entry_id, str) and entry_id == name:
                return entry
    return None


def _resource_named(items: object, name: str) -> bool:
    if not isinstance(items, list):
        return False
    for entry in items:
        if isinstance(entry, dict):
            entry_name = entry.get("name")
            if isinstance(entry_name, str) and entry_name == name:
                return True
            entry_id = entry.get("id")
            if isinstance(entry_id, str) and entry_id == name:
                return True
    return False


async def _get_json(client: httpx.AsyncClient, path: str) -> object:
    response = await client.get(_dashboard_url(path), auth=_auth())
    response.raise_for_status()
    return response.json()


async def _put_json(client: httpx.AsyncClient, path: str, body: object) -> None:
    logger.info("EMQX rule setup PUT %s request_body=%s", path, body)
    response = await client.put(_dashboard_url(path), auth=_auth(), json=body)
    if response.status_code in (200, 204):
        return
    logger.error(
        "EMQX rule setup PUT %s HTTP %s response_body=%s",
        path,
        response.status_code,
        response.text,
    )
    response.raise_for_status()


async def _post_json(client: httpx.AsyncClient, path: str, body: object) -> None:
    logger.info("EMQX rule setup POST %s request_body=%s", path, body)
    response = await client.post(_dashboard_url(path), auth=_auth(), json=body)
    if response.status_code in (200, 201):
        return
    if response.status_code == 400 and "ALREADY_EXISTS" in response.text:
        logger.info("EMQX rule setup POST %s already exists", path)
        return
    logger.error(
        "EMQX rule setup POST %s HTTP %s response_body=%s",
        path,
        response.status_code,
        response.text,
    )
    response.raise_for_status()


def _http_connector_body() -> _HttpConnectorBody:
    base_url, _path = _ingest_webhook_parts()
    return {
        "type": "http",
        "name": CONNECTOR_NAME,
        "enable": True,
        "url": base_url,
        "connect_timeout": "15s",
        "pool_type": "random",
        "pool_size": 8,
        "enable_pipelining": 100,
        "ssl": {"enable": False},
    }


def _http_action_body() -> _HttpActionBody:
    _base, ingest_path = _ingest_webhook_parts()
    secret = settings.mqtt_webhook_shared_secret
    return {
        "type": "http",
        "name": ACTION_NAME,
        "connector": CONNECTOR_NAME,
        "parameters": {
            "method": "post",
            "path": ingest_path,
            "body": ACTION_INGEST_BODY_TEMPLATE,
            "headers": {
                "content-type": "application/json",
                "x-internal-secret": secret,
            },
            "max_retries": 2,
        },
    }


def _http_action_put_body(desired: _HttpActionBody) -> _HttpActionPutBody:
    return {
        "connector": desired["connector"],
        "parameters": desired["parameters"],
    }


def _http_action_needs_update(existing: dict[str, object], desired: _HttpActionBody) -> bool:
    params = existing.get("parameters")
    if not isinstance(params, dict):
        return True
    desired_params = desired["parameters"]
    if params.get("body") != desired_params["body"]:
        return True
    if params.get("path") != desired_params["path"]:
        return True
    existing_headers = params.get("headers")
    if not isinstance(existing_headers, dict):
        return True
    return existing_headers != desired_params["headers"]


def _rule_body() -> _RuleBody:
    return {
        "name": RULE_NAME,
        "enable": True,
        "sql": RULE_SQL,
        "actions": [HTTP_ACTION_REF],
    }


async def _ensure_http_connector(client: httpx.AsyncClient) -> None:
    existing = _items_from_list_response(await _get_json(client, "/api/v5/connectors"))
    if _resource_named(existing, CONNECTOR_NAME):
        return
    await _post_json(client, "/api/v5/connectors", _http_connector_body())


async def _ensure_http_action(client: httpx.AsyncClient) -> None:
    existing_list = _items_from_list_response(await _get_json(client, "/api/v5/actions"))
    desired = _http_action_body()
    found = _find_resource_named(existing_list, ACTION_NAME)
    if found is not None:
        if _http_action_needs_update(found, desired):
            await _put_json(
                client,
                f"/api/v5/actions/{HTTP_ACTION_REF}",
                _http_action_put_body(desired),
            )
        return
    await _post_json(client, "/api/v5/actions", desired)


async def _ensure_rule(client: httpx.AsyncClient) -> None:
    existing = _items_from_list_response(await _get_json(client, "/api/v5/rules"))
    if _resource_named(existing, RULE_NAME):
        return
    await _post_json(client, "/api/v5/rules", _rule_body())


async def _run_setup_once(client: httpx.AsyncClient) -> None:
    await _ensure_http_connector(client)
    await _ensure_http_action(client)
    await _ensure_rule(client)


def _log_http_failure(exc: httpx.HTTPError) -> None:
    if isinstance(exc, httpx.HTTPStatusError) and exc.response.status_code == 401:
        logger.error("%s (api_key prefix=%s)", _AUTH_FAILURE_MESSAGE, _api_key_log_prefix())
        return
    if isinstance(exc, httpx.HTTPStatusError):
        logger.error(
            "EMQX rule setup failed HTTP %s response_body=%s",
            exc.response.status_code,
            exc.response.text,
        )
        return
    logger.warning("EMQX rule setup skipped (unreachable or misconfigured): %s", exc)


async def setup_telemetry_forwarding_rule() -> None:
    if not settings.emqx_telemetry_rule_setup_enabled:
        return
    validate_emqx_api_credentials()
    logger.info(
        "EMQX rule setup using API key prefix=%s (from EMQX_API_KEY env)",
        _api_key_log_prefix(),
    )
    backoff_seconds = (0.0, 2.0, 4.0)
    last_error: httpx.HTTPError | None = None
    for attempt, delay in enumerate(backoff_seconds, start=1):
        if delay > 0:
            await asyncio.sleep(delay)
        try:
            async with httpx.AsyncClient(timeout=settings.emqx_dashboard_timeout_seconds) as client:
                await _run_setup_once(client)
            logger.info("EMQX rule setup OK (%s)", RULE_NAME)
            return
        except httpx.HTTPStatusError as exc:
            last_error = exc
            if exc.response.status_code == 401:
                _log_http_failure(exc)
                return
            logger.warning(
                "EMQX rule setup attempt %s failed HTTP %s: %s",
                attempt,
                exc.response.status_code,
                exc.response.text,
            )
        except httpx.HTTPError as exc:
            last_error = exc
            logger.warning("EMQX rule setup attempt %s failed: %s", attempt, exc)
    if last_error is not None:
        _log_http_failure(last_error)
