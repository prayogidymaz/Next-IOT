"""Docker Compose MQTT port mapping (Windows Mosquitto conflict workaround)."""

from __future__ import annotations

import re
from pathlib import Path

CONTAINER_COMPOSE = Path("/docker-compose.yml")
DEFAULT_EXTERNAL_MQTT_PORT = "11883"
CONTAINER_INTERNAL_MQTT_PORT = "1883"


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


def _web_compose_section(compose_text: str) -> str:
    marker = "  web:"
    start = compose_text.index(marker)
    tail = compose_text[start:]
    end = tail.find("\n  tile-server:")
    if end == -1:
        return tail
    return tail[:end]


def test_mqtt_external_port_is_11883_by_default() -> None:
    section = _emqx_compose_section(_compose_text())
    assert f'"${{MQTT_PORT:-{DEFAULT_EXTERNAL_MQTT_PORT}}}:{CONTAINER_INTERNAL_MQTT_PORT}"' in section


def test_internal_container_port_is_1883() -> None:
    section = _emqx_compose_section(_compose_text())
    match = re.search(r"\$\{MQTT_PORT:-\d+\}:(\d+)", section)
    assert match is not None
    assert match.group(1) == CONTAINER_INTERNAL_MQTT_PORT


def _repo_root() -> Path:
    if CONTAINER_COMPOSE.is_file():
        return CONTAINER_COMPOSE.parent
    return Path(__file__).resolve().parents[3]


def test_env_var_can_override_mqtt_port() -> None:
    compose_text = _compose_text()
    assert "${MQTT_PORT:-11883}" in compose_text
    env_example_path = _repo_root() / ".env.example"
    if env_example_path.is_file():
        assert "MQTT_PORT=11883" in env_example_path.read_text(encoding="utf-8")


def test_web_mqtt_broker_url_uses_mqtt_port_default() -> None:
    section = _web_compose_section(_compose_text())
    expected = (
        f"NEXT_PUBLIC_MQTT_BROKER_URL: mqtt://localhost:${{MQTT_PORT:-{DEFAULT_EXTERNAL_MQTT_PORT}}}"
    )
    assert expected in section
