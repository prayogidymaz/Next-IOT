"""Idempotent EMQX Dashboard API setup for telemetry HTTP forwarding."""

from __future__ import annotations

import asyncio
import logging
from typing import TypedDict

import httpx
from app.config import settings

logger = logging.getLogger(__name__)

CONNECTOR_NAME = "api_mqtt_ingest"
ACTION_NAME = "forward_telemetry"
RULE_ID = "rule_forward_telemetry"
RULE_SQL = 'SELECT topic, payload, clientid, username FROM "tenants/+/devices/+/telemetry"'

_AUTH_FAILURE_MESSAGE = (
    "EMQX API auth failed. Check EMQX_API_KEY env match "
    "EMQX_API_KEY__BOOTSTRAP_FILE di emqx service"
)


class _HttpConnectorBody(TypedDict):
    type: str
    name: str
    enable: bool
    url: str
    method: str
    headers: dict[str, str]


class _HttpActionBody(TypedDict):
    name: str
    type: str
    connector: str
    enable: bool
    parameters: dict[str, str | dict[str, str]]
    resource_opts: dict[str, str | int]


class _RuleBody(TypedDict):
    id: str
    sql: str
    actions: list[str]
    enable: bool


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


async def _post_json(client: httpx.AsyncClient, path: str, body: object) -> None:
    response = await client.post(_dashboard_url(path), auth=_auth(), json=body)
    if response.status_code in (200, 201):
        return
    if response.status_code == 400 and "ALREADY_EXISTS" in response.text:
        return
    response.raise_for_status()


async def _ensure_http_connector(client: httpx.AsyncClient) -> None:
    existing = await _get_json(client, "/api/v5/connectors")
    if _resource_named(existing, CONNECTOR_NAME):
        return
    secret = settings.mqtt_webhook_shared_secret
    body: _HttpConnectorBody = {
        "type": "http",
        "name": CONNECTOR_NAME,
        "enable": True,
        "url": settings.emqx_ingest_webhook_url,
        "method": "post",
        "headers": {
            "content-type": "application/json",
            "x-internal-secret": secret,
        },
    }
    await _post_json(client, "/api/v5/connectors", body)


async def _ensure_http_action(client: httpx.AsyncClient) -> None:
    existing = await _get_json(client, "/api/v5/actions")
    if _resource_named(existing, ACTION_NAME):
        return
    body: _HttpActionBody = {
        "name": ACTION_NAME,
        "type": "http",
        "connector": CONNECTOR_NAME,
        "enable": True,
        "parameters": {
            "method": "post",
            "path": "",
            "headers": {"content-type": "application/json"},
            "body": (
                '{"topic":"${topic}","payload":${payload},'
                '"clientid":"${clientid}","username":"${username}"}'
            ),
        },
        "resource_opts": {
            "worker_pool_size": 8,
            "health_check_interval": "15s",
        },
    }
    await _post_json(client, "/api/v5/actions", body)


async def _ensure_rule(client: httpx.AsyncClient) -> None:
    existing = await _get_json(client, "/api/v5/rules")
    if _resource_named(existing, RULE_ID):
        return
    body: _RuleBody = {
        "id": RULE_ID,
        "sql": RULE_SQL,
        "actions": [ACTION_NAME],
        "enable": True,
    }
    await _post_json(client, "/api/v5/rules", body)


async def _run_setup_once(client: httpx.AsyncClient) -> None:
    await _ensure_http_connector(client)
    await _ensure_http_action(client)
    await _ensure_rule(client)


def _log_http_failure(exc: httpx.HTTPError) -> None:
    if isinstance(exc, httpx.HTTPStatusError) and exc.response.status_code == 401:
        logger.error("%s (api_key prefix=%s)", _AUTH_FAILURE_MESSAGE, _api_key_log_prefix())
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
            logger.info("EMQX rule setup OK (%s)", RULE_ID)
            return
        except httpx.HTTPStatusError as exc:
            last_error = exc
            if exc.response.status_code == 401:
                _log_http_failure(exc)
                return
            logger.warning("EMQX rule setup attempt %s failed: %s", attempt, exc)
        except httpx.HTTPError as exc:
            last_error = exc
            logger.warning("EMQX rule setup attempt %s failed: %s", attempt, exc)
    if last_error is not None:
        _log_http_failure(last_error)
