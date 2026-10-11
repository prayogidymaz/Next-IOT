import { getApiBaseUrl } from "@/lib/auth/api";
import { ACCESS_TOKEN_COOKIE } from "@/lib/auth/constants";
import { z } from "zod";

const alarmItemSchema = z.object({
  id: z.string(),
  severity: z.string(),
  status: z.string(),
  title: z.string(),
  message: z.string().nullable(),
  device_id: z.string().nullable(),
  occurred_at: z.string(),
  escalation_count: z.number(),
});

const alarmListSchema = z.object({
  items: z.array(alarmItemSchema),
  total: z.number(),
});

export type AlarmItem = z.infer<typeof alarmItemSchema>;

function authHeaders(): HeadersInit {
  const prefix = `${ACCESS_TOKEN_COOKIE}=`;
  const match = document.cookie.split(";").map((c) => c.trim()).find((c) => c.startsWith(prefix));
  const token = match ? decodeURIComponent(match.slice(prefix.length)) : null;
  if (!token) throw new Error("Belum masuk");
  return { Accept: "application/json", "Content-Type": "application/json", Authorization: `Bearer ${token}` };
}

export async function listAlarms(params?: {
  status?: string;
  severity?: string;
}): Promise<AlarmItem[]> {
  const qs = new URLSearchParams();
  if (params?.status) qs.set("status", params.status);
  if (params?.severity) qs.set("severity", params.severity);
  const suffix = qs.toString() ? `?${qs.toString()}` : "";
  const res = await fetch(`${getApiBaseUrl()}/api/v1/alarms${suffix}`, { headers: authHeaders() });
  if (!res.ok) throw new Error(`Gagal memuat alarms (${res.status})`);
  return alarmListSchema.parse(await res.json()).items;
}

export async function acknowledgeAlarm(id: string, note?: string): Promise<void> {
  const res = await fetch(`${getApiBaseUrl()}/api/v1/alarms/${id}/acknowledge`, {
    method: "POST",
    headers: authHeaders(),
    body: JSON.stringify({ note: note ?? null }),
  });
  if (!res.ok) throw new Error("Ack gagal");
}

export async function resolveAlarm(id: string, note?: string): Promise<void> {
  const res = await fetch(`${getApiBaseUrl()}/api/v1/alarms/${id}/resolve`, {
    method: "POST",
    headers: authHeaders(),
    body: JSON.stringify({ note: note ?? null }),
  });
  if (!res.ok) throw new Error("Resolve gagal");
}
