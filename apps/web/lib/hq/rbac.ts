export function canWriteDeviceProfiles(role: string | undefined): boolean {
  return role === "tenant_admin" || role === "super_admin";
}

export function canManageMqttCredentials(role: string | undefined): boolean {
  return role === "tenant_admin" || role === "operator" || role === "super_admin";
}

export function canAdminClaimTokens(role: string | undefined): boolean {
  return role === "tenant_admin" || role === "super_admin";
}

export const RBAC_DENIED_MESSAGE = "Hak akses tidak cukup — hanya tenant admin yang dapat mengubah profil.";
