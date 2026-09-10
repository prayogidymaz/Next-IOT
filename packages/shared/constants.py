"""Shared constants for Next-IOT platform."""

APP_NAME = "Next-IOT"
API_VERSION = "v1"

# Security tiers (ref: Executive_Master_Plan_Security_Tiering.pdf)
SECURITY_TIERS = ("free", "pro", "enterprise")

# User roles (ref: core auth module)
USER_ROLES = ("super_admin", "tenant_admin", "operator", "viewer")

# Device status (ref: Device Lifecycle module)
DEVICE_STATUSES = ("pending", "provisioned", "online", "offline", "deactivated")
