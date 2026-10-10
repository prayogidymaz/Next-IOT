"""EMQX Dashboard rule setup (mocked HTTP)."""

from __future__ import annotations

from unittest.mock import patch

import httpx
import pytest
from app.mqtt_auth import emqx_rule_setup


@pytest.fixture(autouse=True)
def _enable_emqx_rule_setup_for_tests(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(emqx_rule_setup.settings, "emqx_telemetry_rule_setup_enabled", True)


class _FakeResponse:
    def __init__(self, status_code: int, payload: object) -> None:
        self.status_code = status_code
        self._payload = payload
        self.text = str(payload)

    def json(self) -> object:
        return self._payload

    def raise_for_status(self) -> None:
        if self.status_code >= 400:
            raise httpx.HTTPStatusError("error", request=httpx.Request("GET", "http://test"), response=self)


class _FakeAsyncClient:
    def __init__(self, *, timeout: float = 10.0) -> None:
        self.timeout = timeout
        self.posts: list[tuple[str, object]] = []
        self.puts: list[tuple[str, object]] = []
        self.gets: list[str] = []

    async def __aenter__(self) -> _FakeAsyncClient:
        return self

    async def __aexit__(self, *_args: object) -> None:
        return None

    async def get(self, url: str, auth: httpx.Auth | tuple[str, str] | None = None) -> _FakeResponse:
        self.gets.append(url)
        if url.endswith("/api/v5/connectors"):
            return _FakeResponse(200, [])
        if url.endswith("/api/v5/actions"):
            return _FakeResponse(200, [])
        if url.endswith("/api/v5/rules"):
            return _FakeResponse(200, [])
        return _FakeResponse(200, [])

    async def post(
        self,
        url: str,
        auth: httpx.Auth | tuple[str, str] | None = None,
        json: object = None,
    ) -> _FakeResponse:
        self.posts.append((url, json))
        return _FakeResponse(201, {})

    async def put(
        self,
        url: str,
        auth: httpx.Auth | tuple[str, str] | None = None,
        json: object = None,
    ) -> _FakeResponse:
        self.puts.append((url, json))
        return _FakeResponse(204, {})


def _authorization_header(auth: httpx.Auth | tuple[str, str] | None) -> str:
    request = httpx.Request("GET", "http://emqx.test")
    if auth is None:
        return request.headers.get("Authorization", "")
    flow = auth.sync_auth_flow(request)
    next(flow)
    return request.headers["Authorization"]


@pytest.mark.asyncio
async def test_setup_creates_connector_if_not_exists(monkeypatch: pytest.MonkeyPatch) -> None:
    fake = _FakeAsyncClient(timeout=1.0)
    monkeypatch.setattr(emqx_rule_setup.httpx, "AsyncClient", lambda **kwargs: fake)
    await emqx_rule_setup.setup_telemetry_forwarding_rule()
    connector_posts = [p for p in fake.posts if p[0].endswith("/api/v5/connectors")]
    assert len(connector_posts) == 1


@pytest.mark.asyncio
async def test_setup_skips_rule_if_paginated_list_has_name(monkeypatch: pytest.MonkeyPatch) -> None:
    class _PagedRulesClient(_FakeAsyncClient):
        async def get(self, url: str, auth: httpx.Auth | tuple[str, str] | None = None) -> _FakeResponse:
            if url.endswith("/api/v5/rules"):
                return _FakeResponse(200, {"data": [{"name": emqx_rule_setup.RULE_NAME}]})
            return await super().get(url, auth)

    fake = _PagedRulesClient(timeout=1.0)
    monkeypatch.setattr(emqx_rule_setup.httpx, "AsyncClient", lambda **kwargs: fake)
    await emqx_rule_setup.setup_telemetry_forwarding_rule()
    rule_posts = [p for p in fake.posts if p[0].endswith("/api/v5/rules")]
    assert len(rule_posts) == 0


@pytest.mark.asyncio
async def test_setup_skips_connector_if_exists(monkeypatch: pytest.MonkeyPatch) -> None:
    class _ExistingClient(_FakeAsyncClient):
        async def get(self, url: str, auth: httpx.Auth | tuple[str, str] | None = None) -> _FakeResponse:
            if url.endswith("/api/v5/connectors"):
                return _FakeResponse(200, [{"name": emqx_rule_setup.CONNECTOR_NAME}])
            return await super().get(url, auth)

    fake = _ExistingClient(timeout=1.0)
    monkeypatch.setattr(emqx_rule_setup.httpx, "AsyncClient", lambda **kwargs: fake)
    await emqx_rule_setup.setup_telemetry_forwarding_rule()
    connector_posts = [p for p in fake.posts if p[0].endswith("/api/v5/connectors")]
    assert len(connector_posts) == 0


@pytest.mark.asyncio
async def test_setup_creates_action(monkeypatch: pytest.MonkeyPatch) -> None:
    fake = _FakeAsyncClient(timeout=1.0)
    monkeypatch.setattr(emqx_rule_setup.httpx, "AsyncClient", lambda **kwargs: fake)
    await emqx_rule_setup.setup_telemetry_forwarding_rule()
    action_posts = [p for p in fake.posts if p[0].endswith("/api/v5/actions")]
    assert len(action_posts) == 1


@pytest.mark.asyncio
async def test_setup_creates_rule_with_correct_sql(monkeypatch: pytest.MonkeyPatch) -> None:
    fake = _FakeAsyncClient(timeout=1.0)
    monkeypatch.setattr(emqx_rule_setup.httpx, "AsyncClient", lambda **kwargs: fake)
    await emqx_rule_setup.setup_telemetry_forwarding_rule()
    rule_posts = [p for p in fake.posts if p[0].endswith("/api/v5/rules")]
    assert len(rule_posts) == 1
    body = rule_posts[0][1]
    assert isinstance(body, dict)
    assert body.get("sql") == emqx_rule_setup.RULE_SQL


@pytest.mark.asyncio
async def test_setup_connector_body_matches_emqx_58_schema(monkeypatch: pytest.MonkeyPatch) -> None:
    fake = _FakeAsyncClient(timeout=1.0)
    monkeypatch.setattr(emqx_rule_setup.httpx, "AsyncClient", lambda **kwargs: fake)
    await emqx_rule_setup.setup_telemetry_forwarding_rule()
    connector_posts = [p for p in fake.posts if p[0].endswith("/api/v5/connectors")]
    body = connector_posts[0][1]
    assert isinstance(body, dict)
    assert body["type"] == "http"
    assert body["name"] == emqx_rule_setup.CONNECTOR_NAME
    assert body["url"] == "http://api:8000"
    assert body["ssl"] == {"enable": False}
    assert "method" not in body
    assert "headers" not in body


@pytest.mark.asyncio
async def test_setup_action_splits_url_and_path(monkeypatch: pytest.MonkeyPatch) -> None:
    fake = _FakeAsyncClient(timeout=1.0)
    monkeypatch.setattr(emqx_rule_setup.httpx, "AsyncClient", lambda **kwargs: fake)
    await emqx_rule_setup.setup_telemetry_forwarding_rule()
    action_posts = [p for p in fake.posts if p[0].endswith("/api/v5/actions")]
    body = action_posts[0][1]
    assert isinstance(body, dict)
    assert body["connector"] == emqx_rule_setup.CONNECTOR_NAME
    params = body["parameters"]
    assert isinstance(params, dict)
    assert params["path"] == "/api/v1/mqtt/ingest/telemetry"
    assert params["body"] == emqx_rule_setup.ACTION_INGEST_BODY_TEMPLATE
    assert params["body"] == "${.}"
    assert params["max_retries"] == 2
    assert params["headers"]["x-internal-secret"] == emqx_rule_setup.settings.mqtt_webhook_shared_secret


@pytest.mark.asyncio
async def test_setup_puts_action_when_existing_body_uses_explicit_field_template(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    stale_body = (
        '{"topic":"${topic}","payload":${payload},'
        '"clientid":"${clientid}","username":"${username}"}'
    )

    class _StaleActionClient(_FakeAsyncClient):
        async def get(self, url: str, auth: httpx.Auth | tuple[str, str] | None = None) -> _FakeResponse:
            if url.endswith("/api/v5/actions"):
                return _FakeResponse(
                    200,
                    [
                        {
                            "name": emqx_rule_setup.ACTION_NAME,
                            "parameters": {
                                "method": "post",
                                "path": "/api/v1/mqtt/ingest/telemetry",
                                "body": stale_body,
                                "headers": {"content-type": "application/json"},
                            },
                        }
                    ],
                )
            return await super().get(url, auth)

    fake = _StaleActionClient(timeout=1.0)
    monkeypatch.setattr(emqx_rule_setup.httpx, "AsyncClient", lambda **kwargs: fake)
    await emqx_rule_setup.setup_telemetry_forwarding_rule()
    assert len([p for p in fake.posts if p[0].endswith("/api/v5/actions")]) == 0
    action_puts = [
        p for p in fake.puts if p[0].endswith(f"/api/v5/actions/{emqx_rule_setup.HTTP_ACTION_REF}")
    ]
    assert len(action_puts) == 1
    put_body = action_puts[0][1]
    assert isinstance(put_body, dict)
    params = put_body["parameters"]
    assert isinstance(params, dict)
    assert params["body"] == emqx_rule_setup.ACTION_INGEST_BODY_TEMPLATE


@pytest.mark.asyncio
async def test_setup_rule_uses_http_action_reference(monkeypatch: pytest.MonkeyPatch) -> None:
    fake = _FakeAsyncClient(timeout=1.0)
    monkeypatch.setattr(emqx_rule_setup.httpx, "AsyncClient", lambda **kwargs: fake)
    await emqx_rule_setup.setup_telemetry_forwarding_rule()
    rule_posts = [p for p in fake.posts if p[0].endswith("/api/v5/rules")]
    body = rule_posts[0][1]
    assert isinstance(body, dict)
    assert body.get("name") == emqx_rule_setup.RULE_NAME
    assert body.get("actions") == [emqx_rule_setup.HTTP_ACTION_REF]
    assert "id" not in body


@pytest.mark.asyncio
async def test_setup_logs_warning_on_emqx_unreachable(monkeypatch: pytest.MonkeyPatch) -> None:
    class _FailClient:
        async def __aenter__(self) -> _FailClient:
            return self

        async def __aexit__(self, *_args: object) -> None:
            return None

        async def get(self, url: str, auth: httpx.Auth | tuple[str, str] | None = None) -> _FakeResponse:
            raise httpx.ConnectError("down")

    monkeypatch.setattr(emqx_rule_setup.httpx, "AsyncClient", lambda **kwargs: _FailClient())
    with patch.object(emqx_rule_setup.logger, "warning") as warn:
        await emqx_rule_setup.setup_telemetry_forwarding_rule()
    assert warn.call_count >= 1


def test_setup_fails_without_api_key(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(emqx_rule_setup.settings, "emqx_api_key", "")
    with pytest.raises(ValueError, match="EMQX_API_KEY and EMQX_API_SECRET are required"):
        emqx_rule_setup.validate_emqx_api_credentials()


@pytest.mark.asyncio
async def test_setup_uses_api_key_auth(monkeypatch: pytest.MonkeyPatch) -> None:
    captured: list[httpx.Auth | tuple[str, str] | None] = []

    class _AuthCapturingClient(_FakeAsyncClient):
        async def get(self, url: str, auth: httpx.Auth | tuple[str, str] | None = None) -> _FakeResponse:
            captured.append(auth)
            return await super().get(url, auth)

    fake = _AuthCapturingClient(timeout=1.0)
    monkeypatch.setattr(emqx_rule_setup.httpx, "AsyncClient", lambda **kwargs: fake)
    await emqx_rule_setup.setup_telemetry_forwarding_rule()
    assert captured
    assert _authorization_header(captured[0]) == _authorization_header(emqx_rule_setup._auth())


@pytest.mark.asyncio
async def test_setup_logs_api_key_prefix_on_401(monkeypatch: pytest.MonkeyPatch) -> None:
    class _UnauthorizedClient(_FakeAsyncClient):
        async def get(self, url: str, auth: httpx.Auth | tuple[str, str] | None = None) -> _FakeResponse:
            return _FakeResponse(401, {})

    monkeypatch.setattr(emqx_rule_setup.httpx, "AsyncClient", lambda **kwargs: _UnauthorizedClient())
    with patch.object(emqx_rule_setup.logger, "error") as err:
        await emqx_rule_setup.setup_telemetry_forwarding_rule()
    assert err.call_count == 1
    log_args = err.call_args[0]
    assert log_args[0] == "%s (api_key prefix=%s)"
    assert "EMQX API auth failed" in log_args[1]
    assert log_args[2]
