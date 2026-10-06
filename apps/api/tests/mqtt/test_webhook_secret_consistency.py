"""Guard: API webhook secret must match EMQX cluster-override.conf literals."""

from __future__ import annotations

import re
from pathlib import Path

from app.config import settings

CONTAINER_EMQX_ROOT = Path("/infra/emqx")
CLUSTER_OVERRIDE_FILE = "cluster-override.conf"
_SECRET_HEADER_PATTERN = re.compile(r'"x-internal-secret"\s*=\s*"([^"]+)"')


def _cluster_override_path() -> Path:
    if CONTAINER_EMQX_ROOT.is_dir():
        return CONTAINER_EMQX_ROOT / CLUSTER_OVERRIDE_FILE
    return Path(__file__).resolve().parents[3] / "infra" / "emqx" / CLUSTER_OVERRIDE_FILE


def test_api_env_secret_matches_emqx_config_file() -> None:
    text = _cluster_override_path().read_text(encoding="utf-8")
    secrets_in_file = _SECRET_HEADER_PATTERN.findall(text)
    assert len(secrets_in_file) == 2
    expected = settings.mqtt_webhook_shared_secret
    assert all(value == expected for value in secrets_in_file)
    assert "${MQTT_WEBHOOK_SHARED_SECRET}" not in text
