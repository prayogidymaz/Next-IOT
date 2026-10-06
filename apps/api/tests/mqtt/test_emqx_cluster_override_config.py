"""EMQX cluster-override.conf layout (infra only)."""

from __future__ import annotations

from pathlib import Path

CONTAINER_EMQX_ROOT = Path("/infra/emqx")
CONTAINER_COMPOSE = Path("/docker-compose.yml")
CLUSTER_OVERRIDE_FILE = "cluster-override.conf"
CLUSTER_OVERRIDE_MOUNT = (
    "./infra/emqx/cluster-override.conf:/opt/emqx/data/configs/cluster-override.conf"
)
AUTH_URL = "http://api:8000/api/v1/mqtt/auth"
ACL_URL = "http://api:8000/api/v1/mqtt/acl"


def _repo_emqx_root() -> Path:
    if CONTAINER_EMQX_ROOT.is_dir() and CONTAINER_COMPOSE.is_file():
        return CONTAINER_EMQX_ROOT
    return Path(__file__).resolve().parents[3] / "infra" / "emqx"


def _cluster_override_path() -> Path:
    return _repo_emqx_root() / CLUSTER_OVERRIDE_FILE


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


def _override_text() -> str:
    return _cluster_override_path().read_text(encoding="utf-8")


def test_cluster_override_file_exists() -> None:
    assert _cluster_override_path().is_file()


def test_cluster_override_contains_authentication_block() -> None:
    assert "authentication = [" in _override_text()


def test_cluster_override_contains_authorization_block() -> None:
    assert "authorization {" in _override_text()


def test_cluster_override_authn_url_points_to_api() -> None:
    text = _override_text()
    assert f'url = "{AUTH_URL}"' in text
    assert "backend = http" in text


def test_cluster_override_authz_no_match_is_deny() -> None:
    text = _override_text()
    assert "no_match = deny" in text
    assert f'url = "{ACL_URL}"' in text


def test_cluster_override_has_secret_header() -> None:
    text = _override_text()
    assert '"x-internal-secret"' in text
    assert "${MQTT_WEBHOOK_SHARED_SECRET}" in text


def test_docker_compose_mounts_cluster_override() -> None:
    section = _emqx_compose_section(_compose_text())
    assert CLUSTER_OVERRIDE_MOUNT in section
    assert "emqx.conf.d" not in section
    assert "/opt/emqx/etc/emqx.conf:ro" not in section
