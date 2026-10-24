"""Universal device mesh — capability registry and cross-domain helpers."""

from app.mesh.capabilities import (
    CAPABILITY_KEYS,
    devices_with_capability,
    infer_capabilities_from_profile,
    validate_capability,
)

__all__ = [
    "CAPABILITY_KEYS",
    "validate_capability",
    "infer_capabilities_from_profile",
    "devices_with_capability",
]
