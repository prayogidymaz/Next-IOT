"""Render PlatformIO project ZIP from Device Profile + studio config."""

from __future__ import annotations

import io
import json
import uuid
import zipfile
from pathlib import Path

from jinja2 import Environment, FileSystemLoader, StrictUndefined
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.dependencies import CurrentUser
from app.device_profiles.service import _get_profile_for_user
from app.firmware_studio.schemas import FirmwareGenerateRequest, FirmwarePreviewResponse, FirmwareStudioConfig
from app.firmware_studio.sensor_drivers import resolve_driver
from app.models.device_profile import DeviceProfile


def _resolve_sdk_root() -> Path:
    here = Path(__file__).resolve()
    candidates: list[Path] = [Path("/firmware/next-iot-esp32-sdk")]
    for depth in range(2, min(8, len(here.parents))):
        candidates.append(here.parents[depth] / "firmware" / "next-iot-esp32-sdk")
    for candidate in candidates:
        if candidate.is_dir():
            return candidate
    return candidates[0]


_TEMPLATE_DIR = Path(__file__).resolve().parent / "templates"

_jinja = Environment(
    loader=FileSystemLoader(str(_TEMPLATE_DIR)),
    undefined=StrictUndefined,
    autoescape=False,
    keep_trailing_newline=True,
)


def _metric_keys_from_spec(spec: dict[str, object]) -> list[str]:
    telemetry = spec.get("telemetry")
    if not isinstance(telemetry, list):
        return []
    keys: list[str] = []
    for entry in telemetry:
        if isinstance(entry, dict):
            key_raw = entry.get("key")
            if isinstance(key_raw, str) and key_raw:
                keys.append(key_raw)
    return keys


def _build_sensor_context(config: FirmwareStudioConfig) -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []
    seen_dht_pin: int | None = None
    for binding in config.sensors:
        spec = resolve_driver(binding.metric, binding.driver)
        global_decl = spec.global_decl.replace("{pin}", str(binding.pin))
        if binding.driver == "dht22":
            if seen_dht_pin is None:
                seen_dht_pin = binding.pin
            elif seen_dht_pin == binding.pin and "dhtSensor" in global_decl:
                global_decl = ""
        rows.append(
            {
                "metric": binding.metric,
                "driver": binding.driver,
                "pin": str(binding.pin),
                "library": spec.library,
                "include_header": spec.include_header,
                "global_decl": global_decl,
                "init_code": spec.init_code,
                "read_expr": spec.read_expr,
            }
        )
    return rows


def _render_context(profile: DeviceProfile, config: FirmwareStudioConfig) -> dict[str, object]:
    spec = profile.spec if isinstance(profile.spec, dict) else {}
    libraries = sorted(
        {row["library"] for row in _build_sensor_context(config) if row["library"]}
    )
    board_map = {
        "esp32-s3": "esp32-s3-devkitc-1",
        "esp32-c3": "esp32-c3-devkitm-1",
        "esp32-wroom": "esp32dev",
    }
    return {
        "profile_name": profile.name,
        "profile_key": profile.key,
        "profile_version": profile.version,
        "metrics": _metric_keys_from_spec(spec),
        "config": config,
        "sensors": _build_sensor_context(config),
        "libraries": libraries,
        "board": board_map.get(config.mcu.value, "esp32-s3-devkitc-1"),
        "thing_model_json": json.dumps(spec, indent=2),
        "credential_block": _credential_block(config),
    }


def _credential_block(config: FirmwareStudioConfig) -> str:
    if not config.include_credentials:
        return (
            "    // Set via serial provisioning or edit secrets before flash\n"
            '    .tenant_id = "YOUR_TENANT_ID",\n'
            '    .device_id = "YOUR_DEVICE_ID",\n'
            '    .access_token = "YOUR_ACCESS_TOKEN",'
        )
    tenant = str(config.tenant_id) if config.tenant_id else "YOUR_TENANT_ID"
    device = str(config.device_id) if config.device_id else "YOUR_DEVICE_ID"
    token = config.access_token or "YOUR_ACCESS_TOKEN"
    return (
        f'    .tenant_id = "{tenant}",\n'
        f'    .device_id = "{device}",\n'
        f'    .access_token = "{token}",'
    )


def render_preview(profile: DeviceProfile, config: FirmwareStudioConfig) -> FirmwarePreviewResponse:
    ctx = _render_context(profile, config)
    platformio_ini = _jinja.get_template("platformio.ini.j2").render(**ctx)
    main_cpp = _jinja.get_template("main.cpp.j2").render(**ctx)
    readme_md = _jinja.get_template("README.md.j2").render(**ctx)
    return FirmwarePreviewResponse(platformio_ini=platformio_ini, main_cpp=main_cpp, readme_md=readme_md)


def _add_sdk_to_zip(zf: zipfile.ZipFile) -> None:
    sdk_root = _resolve_sdk_root()
    if not sdk_root.is_dir():
        return
    for path in sdk_root.rglob("*"):
        if not path.is_file():
            continue
        if "examples" in path.parts:
            continue
        rel = path.relative_to(sdk_root).as_posix()
        arcname = f"lib/next-iot-esp32-sdk/{rel}"
        zf.writestr(arcname, path.read_bytes())


def build_firmware_zip(profile: DeviceProfile, config: FirmwareStudioConfig) -> bytes:
    for sensor in config.sensors:
        resolve_driver(sensor.metric, sensor.driver)
    preview = render_preview(profile, config)
    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, "w", zipfile.ZIP_DEFLATED) as zf:
        zf.writestr("platformio.ini", preview.platformio_ini)
        zf.writestr("src/main.cpp", preview.main_cpp)
        zf.writestr("README.md", preview.readme_md)
        _add_sdk_to_zip(zf)
    return buffer.getvalue()


async def preview_for_user(
    db: AsyncSession,
    user: CurrentUser,
    payload: FirmwareGenerateRequest,
) -> FirmwarePreviewResponse:
    profile = await _get_profile_for_user(db, payload.device_profile_id, user)
    for sensor in payload.config.sensors:
        resolve_driver(sensor.metric, sensor.driver)
    return render_preview(profile, payload.config)


async def generate_for_user(
    db: AsyncSession,
    user: CurrentUser,
    payload: FirmwareGenerateRequest,
) -> tuple[bytes, str]:
    profile = await _get_profile_for_user(db, payload.device_profile_id, user)
    spec_metrics = set(_metric_keys_from_spec(profile.spec if isinstance(profile.spec, dict) else {}))
    for sensor in payload.config.sensors:
        if spec_metrics and sensor.metric not in spec_metrics:
            raise ValueError(f"Metric '{sensor.metric}' is not defined on profile '{profile.key}'")
        resolve_driver(sensor.metric, sensor.driver)
    if payload.config.include_credentials:
        if not payload.config.tenant_id or not payload.config.device_id or not payload.config.access_token:
            raise ValueError("include_credentials requires tenant_id, device_id, and access_token")
    zip_bytes = build_firmware_zip(profile, payload.config)
    filename = f"next-iot-{profile.key}-v{profile.version}-{uuid.uuid4().hex[:8]}.zip"
    return zip_bytes, filename
