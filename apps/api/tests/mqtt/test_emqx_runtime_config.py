"""Runtime EMQX config verification (requires Docker CLI + running emqx service)."""

from __future__ import annotations

import shutil
import subprocess
from pathlib import Path

import pytest

CONTAINER_COMPOSE = Path("/docker-compose.yml")


def _repo_root() -> Path:
    if CONTAINER_COMPOSE.is_file():
        return CONTAINER_COMPOSE.parent
    start = Path(__file__).resolve()
    for parent in start.parents:
        if (parent / "docker-compose.yml").is_file():
            return parent
    return start.parents[3]


def _docker_compose_available() -> bool:
    compose = _repo_root() / "docker-compose.yml"
    if not compose.is_file():
        return False
    return shutil.which("docker") is not None


def _emqx_conf_show(section: str) -> str | None:
    compose_file = _repo_root() / "docker-compose.yml"
    result = subprocess.run(
        [
            "docker",
            "compose",
            "-f",
            str(compose_file),
            "exec",
            "-T",
            "emqx",
            "emqx",
            "ctl",
            "conf",
            "show",
            section,
        ],
        capture_output=True,
        text=True,
        timeout=60,
        check=False,
    )
    if result.returncode != 0:
        return None
    return result.stdout


@pytest.mark.integration
def test_emqx_container_authentication_loaded() -> None:
    if not _docker_compose_available():
        pytest.skip("docker compose not available for EMQX runtime verification")
    output = _emqx_conf_show("authentication")
    if output is None:
        pytest.skip("EMQX container not running or emqx ctl failed")
    compact = output.replace(" ", "")
    assert compact != "authentication=[]"
    assert "backend=http" in compact or "backend = http" in output
    assert "/api/v1/mqtt/auth" in output
    assert "x-internal-secret = \"dev-mqtt-webhook-secret\"" in output or (
        "x-internal-secret=dev-mqtt-webhook-secret" in output.replace(" ", "")
    )
    assert "${MQTT_WEBHOOK_SHARED_SECRET}" not in output


@pytest.mark.integration
def test_emqx_container_authorization_no_match_deny() -> None:
    if not _docker_compose_available():
        pytest.skip("docker compose not available for EMQX runtime verification")
    output = _emqx_conf_show("authorization")
    if output is None:
        pytest.skip("EMQX container not running or emqx ctl failed")
    assert "no_match = deny" in output or "no_match=deny" in output.replace(" ", "")
    assert "/api/v1/mqtt/acl" in output
    assert "type = http" in output or "type=http" in output.replace(" ", "")
