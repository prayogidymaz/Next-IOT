import 'app_permissions.dart';

/// Client-side fallback when `/users/me/permissions` is still loading.
Set<String> permissionsForRole(String role) {
  final normalized = role.toLowerCase();
  switch (normalized) {
    case 'super_admin':
    case 'tenant_admin':
      return AppPermissions.all;
    case 'operator':
      return {
        AppPermissions.devicesRead,
        AppPermissions.commandsSend,
        AppPermissions.alertsAck,
        AppPermissions.automationRead,
        AppPermissions.automationRun,
      };
    case 'viewer':
      return {
        AppPermissions.devicesRead,
        AppPermissions.automationRead,
        AppPermissions.automationRun,
      };
    default:
      return {AppPermissions.devicesRead};
  }
}

bool roleCan(String role, String permission) =>
    permissionsForRole(role).contains(permission);
