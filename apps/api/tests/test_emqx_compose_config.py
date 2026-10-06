"""EMQX broker compose + HOCON config (no API logic)."""

from __future__ import annotations

from pathlib import Path

CONTAINER_EMQX_CONF = Path("/infra/emqx/emqx.conf")
CONTAINER_COMPOSE = Path("/docker-compose.yml")

EMQX_CONF_MOUNT = "./infra/emqx/emqx.conf:/opt/emqx/etc/emqx.conf:ro"


def _config_paths() -> tuple[Path, Path]:
    if CONTAINER_EMQX_CONF.is_file() and CONTAINER_COMPOSE.is_file():
        return CONTAINER_EMQX_CONF, CONTAINER_COMPOSE
    repo_root = Path(__file__).resolve().parents[3]
    return repo_root / "infra" / "emqx" / "emqx.conf", repo_root / "docker-compose.yml"


def _emqx_compose_section(compose_text: str) -> str:
    marker = "  emqx:"
    start = compose_text.index(marker)
    tail = compose_text[start:]
    end_marker = "\nvolumes:"
    end = tail.find(end_marker)
    if end == -1:
        return tail
    return tail[:end]


def test_emqx_config_file_exists_and_valid_hocon() -> None:
    emqx_conf, _ = _config_paths()
    assert emqx_conf.is_file(), "infra/emqx/emqx.conf must exist"
    text = emqx_conf.read_text(encoding="utf-8")
    assert "authentication = [" in text
    assert "authorization {" in text
    assert 'url = "http://api:8000/api/v1/mqtt/auth"' in text
    assert 'url = "http://api:8000/api/v1/mqtt/acl"' in text
    assert '"x-internal-secret"' in text
    assert "${MQTT_WEBHOOK_SHARED_SECRET}" in text
    assert "EMQX_AUTHENTICATION__" not in text


def test_docker_compose_mounts_emqx_config() -> None:
    _, compose_file = _config_paths()
    text = compose_file.read_text(encoding="utf-8")
    section = _emqx_compose_section(text)
    assert EMQX_CONF_MOUNT in section
    assert "MQTT_WEBHOOK_SHARED_SECRET:" in section
    assert "EMQX_AUTHENTICATION__" not in section
    assert "EMQX_AUTHORIZATION__" not in section
