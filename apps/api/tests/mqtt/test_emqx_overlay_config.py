"""EMQX overlay directory layout (infra only, not API logic)."""

from __future__ import annotations

from pathlib import Path

CONTAINER_EMQX_ROOT = Path("/infra/emqx")
CONTAINER_COMPOSE = Path("/docker-compose.yml")
OVERLAY_MOUNT = "./infra/emqx/overlay:/opt/emqx/etc/emqx.conf.d:ro"
AUTH_OVERLAY_FILE = "10_auth.conf"
AUTH_URL = "http://api:8000/api/v1/mqtt/auth"
ACL_URL = "http://api:8000/api/v1/mqtt/acl"


def _repo_emqx_root() -> Path:
    if CONTAINER_EMQX_ROOT.is_dir() and CONTAINER_COMPOSE.is_file():
        return CONTAINER_EMQX_ROOT
    return Path(__file__).resolve().parents[3] / "infra" / "emqx"


def _compose_text() -> str:
    if CONTAINER_COMPOSE.is_file():
        return CONTAINER_COMPOSE.read_text(encoding="utf-8")
    repo_root = Path(__file__).resolve().parents[3]
    return (repo_root / "docker-compose.yml").read_text(encoding="utf-8")


def _emqx_compose_section(compose_text: str) -> str:
    marker = "  emqx:"
    start = compose_text.index(marker)
    tail = compose_text[start:]
    end = tail.find("\nvolumes:")
    if end == -1:
        return tail
    return tail[:end]


def _auth_overlay_path() -> Path:
    return _repo_emqx_root() / "overlay" / AUTH_OVERLAY_FILE


def test_overlay_directory_exists() -> None:
    overlay_dir = _repo_emqx_root() / "overlay"
    assert overlay_dir.is_dir()


def test_overlay_has_auth_config_file() -> None:
    assert _auth_overlay_path().is_file()


def test_overlay_auth_file_contains_authentication_block() -> None:
    text = _auth_overlay_path().read_text(encoding="utf-8")
    assert "authentication = [" in text


def test_overlay_auth_file_contains_authorization_block() -> None:
    text = _auth_overlay_path().read_text(encoding="utf-8")
    assert "authorization {" in text


def test_overlay_auth_file_references_api_webhook_urls() -> None:
    text = _auth_overlay_path().read_text(encoding="utf-8")
    assert f'url = "{AUTH_URL}"' in text
    assert f'url = "{ACL_URL}"' in text


def test_overlay_auth_file_has_internal_secret_header() -> None:
    text = _auth_overlay_path().read_text(encoding="utf-8")
    assert '"x-internal-secret"' in text
    assert "${MQTT_WEBHOOK_SHARED_SECRET}" in text


def test_docker_compose_mounts_overlay_directory() -> None:
    section = _emqx_compose_section(_compose_text())
    assert OVERLAY_MOUNT in section
    assert "MQTT_WEBHOOK_SHARED_SECRET:" in section
    assert "/opt/emqx/etc/emqx.conf:ro" not in section
