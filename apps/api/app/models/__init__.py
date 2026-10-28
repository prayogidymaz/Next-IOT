"""ORM model registry — import every mapped class so ``Base.metadata`` is complete."""

from app.agriculture.models import (
    AgriCropCalendar,
    AgriDiseaseAlert,
    AgriFarm,
    AgriIrrigationLog,
    AgriIrrigationValve,
    AgriLoraGateway,
    AgriPlot,
    AgriSensorBatteryHistory,
    AgriSensorDevice,
    AgriYieldRecord,
)
from app.analytics.ml.models import AnomalyEventRow, OptimizationReportRow, YieldForecastRow
from app.analytics.models import ScheduledReport
from app.cameras.models import Camera, CameraSnapshot
from app.models.alarm import Alarm, AlarmHistory, AlarmStatus
from app.models.audit_log import AuditLog
from app.models.automation_pipeline import AutomationPipeline
from app.models.device import Device, DeviceStatus
from app.models.device_attribute import DeviceAttribute
from app.models.device_claim_token import DeviceClaimToken
from app.models.device_command import CommandStatus, CommandType, DeviceCommand
from app.models.device_credential import DeviceCredential
from app.models.device_metadata import DeviceMetadata
from app.models.device_profile import DeviceProfile, ProfileDomain, ProfileStatus
from app.models.device_rpc_request import DeviceRpcRequest
from app.models.feature_flag import FeatureFlag
from app.models.firmware_release import FirmwareRelease, OtaDeviceRollout
from app.models.geofence_zone import GeofenceAction, GeofenceZone
from app.models.impersonation_session import ImpersonationSession, ImpersonationSessionAction
from app.models.invoice import Invoice
from app.models.mesh_event import MeshEventRecord
from app.models.mesh_workflow import MeshWorkflow, MeshWorkflowExecution
from app.models.notification_gateway import NotificationChannel, NotificationLog, NotificationRule
from app.models.partner import Partner, PartnerCommission, PartnerReferral
from app.models.payment_method import PaymentMethod
from app.models.platform_announcement import PlatformAnnouncement
from app.models.platform_backup import PlatformBackup
from app.models.platform_email_template import PlatformEmailTemplate
from app.models.platform_setting import PlatformSetting
from app.models.promo_code import PromoCode
from app.models.rule import Rule, RuleActionType, RuleOperator
from app.models.rule_execution_log import RuleExecutionLog
from app.models.sar_incident import SarIncident, SarIncidentStatus, SarIncidentType
from app.models.subscription_plan import SubscriptionPlan
from app.models.super_admin_action import SuperAdminAction
from app.models.support_ticket import SupportTicket, SupportTicketMessage
from app.models.telemetry_anomaly import TelemetryAnomaly
from app.models.telemetry_reading import TelemetryReading
from app.models.tenant import Tenant
from app.models.tenant_membership import TenantMembership
from app.models.tenant_user_fcm_token import TenantUserFcmToken
from app.models.tenant_subscription import TenantSubscription
from app.models.tenant_usage_daily import TenantUsageDaily
from app.models.user import User

__all__ = [
    "Partner",
    "PartnerReferral",
    "PartnerCommission",
    "SubscriptionPlan",
    "PromoCode",
    "FeatureFlag",
    "PlatformSetting",
    "PlatformAnnouncement",
    "PlatformEmailTemplate",
    "PlatformBackup",
    "Tenant",
    "PaymentMethod",
    "TenantSubscription",
    "TenantUsageDaily",
    "Invoice",
    "MeshEventRecord",
    "MeshWorkflow",
    "MeshWorkflowExecution",
    "Camera",
    "CameraSnapshot",
    "ScheduledReport",
    "YieldForecastRow",
    "AnomalyEventRow",
    "OptimizationReportRow",
    "User",
    "TenantMembership",
    "TenantUserFcmToken",
    "DeviceProfile",
    "ProfileDomain",
    "ProfileStatus",
    "Device",
    "DeviceStatus",
    "DeviceAttribute",
    "DeviceRpcRequest",
    "DeviceCredential",
    "DeviceClaimToken",
    "DeviceMetadata",
    "DeviceCommand",
    "CommandType",
    "CommandStatus",
    "FirmwareRelease",
    "OtaDeviceRollout",
    "TelemetryReading",
    "TelemetryAnomaly",
    "Rule",
    "RuleOperator",
    "RuleActionType",
    "RuleExecutionLog",
    "Alarm",
    "AlarmHistory",
    "AlarmStatus",
    "NotificationChannel",
    "NotificationRule",
    "NotificationLog",
    "GeofenceZone",
    "GeofenceAction",
    "SarIncident",
    "SarIncidentType",
    "SarIncidentStatus",
    "AutomationPipeline",
    "AuditLog",
    "SuperAdminAction",
    "SupportTicket",
    "SupportTicketMessage",
    "ImpersonationSession",
    "ImpersonationSessionAction",
    "AgriFarm",
    "AgriPlot",
    "AgriLoraGateway",
    "AgriSensorDevice",
    "AgriIrrigationValve",
    "AgriIrrigationLog",
    "AgriDiseaseAlert",
    "AgriCropCalendar",
    "AgriYieldRecord",
    "AgriSensorBatteryHistory",
]
