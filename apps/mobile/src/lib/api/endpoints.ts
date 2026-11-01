import { apiFetch } from "./client";

export type AuthUser = {
  user_id: string;
  email: string;
  role: string;
  tenant_id: string;
  permissions: string[];
};

export type DeviceRecord = {
  id: string;
  name: string;
  device_type: string;
  online: boolean;
};

export type AlarmRecord = {
  id: string;
  severity: string;
  status: string;
  title: string;
  message: string | null;
  occurred_at: string;
};

export type WorkflowRecord = {
  id: string;
  name: string;
  enabled: boolean;
  last_fired_at?: string | null;
};

export async function login(email: string, password: string): Promise<{ access_token: string; user: AuthUser }> {
  const res = await apiFetch("/api/v1/auth/login", {
    method: "POST",
    auth: false,
    body: JSON.stringify({ email, password }),
  });
  if (!res.ok) throw new Error("Login gagal");
  const tokens = (await res.json()) as { access_token: string };
  const meRes = await apiFetch("/api/v1/auth/me", {
    headers: { Authorization: `Bearer ${tokens.access_token}` },
    auth: false,
  });
  if (!meRes.ok) throw new Error("Profil gagal dimuat");
  const user = (await meRes.json()) as AuthUser;
  return { access_token: tokens.access_token, user };
}

export async function fetchDevices(): Promise<DeviceRecord[]> {
  const res = await apiFetch("/api/v1/devices");
  if (!res.ok) throw new Error("Gagal memuat perangkat");
  const body = (await res.json()) as { items?: DeviceRecord[] } | DeviceRecord[];
  return Array.isArray(body) ? body : (body.items ?? []);
}

export async function fetchAlarms(status?: string): Promise<AlarmRecord[]> {
  const q = status ? `?status=${encodeURIComponent(status)}` : "";
  const res = await apiFetch(`/api/v1/alarms${q}`);
  if (!res.ok) throw new Error("Gagal memuat alert");
  const body = (await res.json()) as { items: AlarmRecord[] };
  return body.items ?? [];
}

export async function fetchWorkflows(): Promise<WorkflowRecord[]> {
  const res = await apiFetch("/api/v1/mesh/workflows");
  if (!res.ok) throw new Error("Gagal memuat workflow");
  const body = (await res.json()) as { items?: WorkflowRecord[] } | WorkflowRecord[];
  return Array.isArray(body) ? body : (body.items ?? []);
}

export async function registerDevice(body: {
  device_token: string;
  device_type: string;
  name?: string;
  capabilities?: string[];
}): Promise<{ id: string }> {
  const res = await apiFetch("/api/v1/devices/register", {
    method: "POST",
    body: JSON.stringify(body),
  });
  if (!res.ok) throw new Error("Registrasi perangkat gagal");
  return (await res.json()) as { id: string };
}

export async function triggerWorkflow(workflowId: string): Promise<void> {
  const res = await apiFetch(`/api/v1/mesh/workflows/${workflowId}/test`, { method: "POST", body: "{}" });
  if (!res.ok) throw new Error("Trigger workflow gagal");
}

export async function sendTestNotification(): Promise<void> {
  const res = await apiFetch("/api/v1/users/me/push-token/test", { method: "POST", body: "{}" });
  if (!res.ok) throw new Error("Test notifikasi gagal");
}

export async function registerPushToken(token: string, platform: "ios" | "android"): Promise<void> {
  const res = await apiFetch("/api/v1/users/me/push-token", {
    method: "POST",
    body: JSON.stringify({ token, platform }),
  });
  if (!res.ok) throw new Error("Gagal mendaftarkan push token");
}
