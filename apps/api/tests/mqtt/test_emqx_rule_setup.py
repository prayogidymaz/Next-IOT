"""EMQX Dashboard rule setup (mocked HTTP)."""

from __future__ import annotations

from unittest.mock import patch

import httpx
import pytest
from app.mqtt_auth import emqx_rule_setup


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
    def __init__(self, *, timeout: float) -> None:
        self.timeout = timeout
        self.posts: list[tuple[str, object]] = []
        self.gets: list[str] = []

    async def __aenter__(self) -> _FakeAsyncClient:
        return self

    async def __aexit__(self, *_args: object) -> None:
        return None

    async def get(self, url: str, auth: tuple[str, str] | None = None) -> _FakeResponse:
        self.gets.append(url)
        if url.endswith("/api/v5/connectors"):
            return _FakeResponse(200, [])
        if url.endswith("/api/v5/actions"):
            return _FakeResponse(200, [])
        if url.endswith("/api/v5/rules"):
            return _FakeResponse(200, [])
        return _FakeResponse(200, [])

    async def post(self, url: str, auth: tuple[str, str] | None = None, json: object = None) -> _FakeResponse:
        self.posts.append((url, json))
        return _FakeResponse(201, {})


@pytest.mark.asyncio
async def test_setup_creates_connector_if_not_exists(monkeypatch: pytest.MonkeyPatch) -> None:
    fake = _FakeAsyncClient(timeout=1.0)
    monkeypatch.setattr(emqx_rule_setup.httpx, "AsyncClient", lambda **kwargs: fake)
    await emqx_rule_setup.setup_telemetry_forwarding_rule()
    connector_posts = [p for p in fake.posts if p[0].endswith("/api/v5/connectors")]
    assert len(connector_posts) == 1


@pytest.mark.asyncio
async def test_setup_skips_connector_if_exists(monkeypatch: pytest.MonkeyPatch) -> None:
    class _ExistingClient(_FakeAsyncClient):
        async def get(self, url: str, auth: tuple[str, str] | None = None) -> _FakeResponse:
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
async def test_setup_logs_warning_on_emqx_unreachable(monkeypatch: pytest.MonkeyPatch) -> None:
    class _FailClient:
        async def __aenter__(self) -> _FailClient:
            return self

        async def __aexit__(self, *_args: object) -> None:
            return None

        async def get(self, url: str, auth: tuple[str, str] | None = None) -> _FakeResponse:
            raise httpx.ConnectError("down")

    monkeypatch.setattr(emqx_rule_setup.httpx, "AsyncClient", lambda **kwargs: _FailClient())
    with patch.object(emqx_rule_setup.logger, "warning") as warn:
        await emqx_rule_setup.setup_telemetry_forwarding_rule()
    warn.assert_called_once()
