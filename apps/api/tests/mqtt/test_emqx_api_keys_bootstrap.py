"""EMQX api-keys.conf bootstrap file (infra only)."""

from __future__ import annotations

from pathlib import Path

CONTAINER_COMPOSE = Path("/docker-compose.yml")
API_KEYS_FILE = "api-keys.conf"
API_KEYS_MOUNT = "./infra/emqx/api-keys.conf:/opt/emqx/etc/api-keys.conf:ro"
BOOTSTRAP_ENV = "EMQX_API_KEY__BOOTSTRAP_FILE: /opt/emqx/etc/api-keys.conf"


def _repo_emqx_dir() -> Path:
    if Path("/infra/emqx").is_dir():
        return Path("/infra/emqx")
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


def test_api_keys_bootstrap_file_has_no_comment_lines() -> None:
    """EMQX 5.8 parses every line; # comments break bootstrap (invalid_role on bracket text)."""
    lines = (_repo_emqx_dir() / API_KEYS_FILE).read_text(encoding="utf-8").splitlines()
    assert lines
    for line in lines:
        stripped = line.strip()
        assert stripped
        assert not stripped.startswith("#"), "api-keys.conf must not contain comment lines"
        assert stripped.count(":") == 1, "expected single key:secret line without optional role suffix"


def test_docker_compose_mounts_api_keys_bootstrap() -> None:
    section = _emqx_compose_section(_compose_text())
    assert API_KEYS_MOUNT in section
    assert BOOTSTRAP_ENV in section


def test_docker_compose_api_passes_emqx_api_key_from_env() -> None:
    compose_text = _compose_text()
    api_start = compose_text.index("  api:")
    api_section = compose_text[api_start : compose_text.index("\n  web:", api_start)]
    assert "EMQX_API_KEY: ${EMQX_API_KEY:-nextiot-api-key}" in api_section
    assert "EMQX_API_SECRET: ${EMQX_API_SECRET:-nextiot-api-secret-change-in-prod}" in api_section
