import { z } from "zod";

import { getApiBaseUrl } from "@/lib/auth/api";
import { readAccessTokenFromDocument } from "@/lib/auth/token-role";

import { formatIdr } from "./super-admin";

export { formatIdr };

function authHeaders(): HeadersInit {
  const token = readAccessTokenFromDocument();
  if (!token) throw new Error("Belum masuk");
  return { Accept: "application/json", Authorization: `Bearer ${token}` };
}

const auditEntrySchema = z.object({
  id: z.string().uuid(),
  timestamp: z.string(),
  actor_type: z.string(),
  actor_label: z.string(),
  action: z.string(),
  target: z.string(),
  details: z.record(z.string(), z.unknown()),
  source: z.string(),
});

export type AuditLogEntry = z.infer<typeof auditEntrySchema>;

export async function fetchAuditLog(params: {
  action?: string;
  limit?: number;
}): Promise<AuditLogEntry[]> {
  const qs = new URLSearchParams();
  if (params.action) qs.set("action", params.action);
  if (params.limit) qs.set("limit", String(params.limit));
  const suffix = qs.toString() ? `?${qs}` : "";
  const res = await fetch(`${getApiBaseUrl()}/api/v1/super-admin/audit-log${suffix}`, { headers: authHeaders() });
  if (!res.ok) throw new Error(String(res.status));
  return z.array(auditEntrySchema).parse(await res.json());
}

export async function downloadAuditLogExport(): Promise<void> {
  const res = await fetch(`${getApiBaseUrl()}/api/v1/super-admin/audit-log/export`, { headers: authHeaders() });
  if (!res.ok) throw new Error(String(res.status));
  const blob = new Blob([await res.text()], { type: "text/csv" });
  const url = URL.createObjectURL(blob);
  const a = document.createElement("a");
  a.href = url;
  a.download = "audit-log.csv";
  a.click();
  URL.revokeObjectURL(url);
}

const analyticsSchema = z.object({
  mrr_trend: z.array(z.object({ month: z.string(), revenue_idr: z.number() })),
  cohort_retention: z.array(
    z.object({
      cohort_month: z.string(),
      tenant_id: z.string().uuid(),
      active_months: z.array(z.string()),
    }),
  ),
  churn_by_plan: z.array(
    z.object({ plan_code: z.string(), churn_rate_percent: z.number(), subscribers: z.number() }),
  ),
  arpa_idr: z.number(),
  ltv_estimate_idr: z.number(),
  device_growth: z.array(z.record(z.string(), z.union([z.string(), z.number()]))),
  message_volume: z.array(z.record(z.string(), z.union([z.string(), z.number()]))),
});

export type AnalyticsDeepDive = z.infer<typeof analyticsSchema>;

export async function fetchAnalyticsDeepDive(): Promise<AnalyticsDeepDive> {
  const res = await fetch(`${getApiBaseUrl()}/api/v1/super-admin/analytics/deep-dive`, { headers: authHeaders() });
  if (!res.ok) throw new Error(String(res.status));
  return analyticsSchema.parse(await res.json());
}

const healthSchema = z.object({
  tenant_id: z.string().uuid(),
  tenant_name: z.string(),
  tenant_slug: z.string(),
  score: z.number(),
  at_risk: z.boolean(),
  device_count: z.number(),
});

export type HealthScoreRow = z.infer<typeof healthSchema>;

export async function fetchHealthScores(): Promise<HealthScoreRow[]> {
  const res = await fetch(`${getApiBaseUrl()}/api/v1/super-admin/health-scores`, { headers: authHeaders() });
  if (!res.ok) throw new Error(String(res.status));
  return z.array(healthSchema).parse(await res.json());
}

const mqttSchema = z.object({
  connections: z.number(),
  messages_per_sec: z.number(),
  status: z.string(),
  errors: z.number(),
});

export type MqttStats = z.infer<typeof mqttSchema>;

export async function fetchMqttStats(): Promise<MqttStats> {
  const res = await fetch(`${getApiBaseUrl()}/api/v1/super-admin/mqtt/stats`, { headers: authHeaders() });
  if (!res.ok) throw new Error(String(res.status));
  return mqttSchema.parse(await res.json());
}

const rateLimitSchema = z.object({
  tenant_id: z.string().uuid(),
  tenant_name: z.string(),
  api_calls_period: z.number(),
  mqtt_messages_period: z.number(),
  quota_usage_percent: z.number(),
  rate_limit_hits: z.number(),
});

export async function fetchRateLimits(): Promise<z.infer<typeof rateLimitSchema>[]> {
  const res = await fetch(`${getApiBaseUrl()}/api/v1/super-admin/rate-limits?period=24h`, { headers: authHeaders() });
  if (!res.ok) throw new Error(String(res.status));
  return z.array(rateLimitSchema).parse(await res.json());
}

export async function fetchSystemLogs(params: {
  service: string;
  level: string;
  lines: number;
}): Promise<{ timestamp: string; level: string; message: string }[]> {
  const qs = new URLSearchParams({
    service: params.service,
    level: params.level,
    lines: String(params.lines),
  });
  const res = await fetch(`${getApiBaseUrl()}/api/v1/super-admin/logs/tail?${qs}`, { headers: authHeaders() });
  if (!res.ok) throw new Error(String(res.status));
  return z
    .array(
      z.object({
        timestamp: z.string(),
        level: z.string(),
        message: z.string(),
      }),
    )
    .parse(await res.json());
}

const announcementSchema = z.object({
  id: z.string().uuid(),
  title: z.string(),
  body: z.string(),
  announcement_type: z.string(),
  target_filter: z.record(z.string(), z.unknown()),
  published: z.boolean(),
});

export async function listAnnouncements(): Promise<z.infer<typeof announcementSchema>[]> {
  const res = await fetch(`${getApiBaseUrl()}/api/v1/super-admin/announcements`, { headers: authHeaders() });
  if (!res.ok) throw new Error(String(res.status));
  return z.array(announcementSchema).parse(await res.json());
}

export async function createAnnouncement(payload: {
  title: string;
  body: string;
  published: boolean;
}): Promise<void> {
  const res = await fetch(`${getApiBaseUrl()}/api/v1/super-admin/announcements`, {
    method: "POST",
    headers: { ...authHeaders(), "Content-Type": "application/json" },
    body: JSON.stringify({
      title: payload.title,
      body: payload.body,
      announcement_type: "info",
      target_filter: { scope: "all" },
      published: payload.published,
    }),
  });
  if (!res.ok) throw new Error(await res.text());
}

const promoSchema = z.object({
  id: z.string().uuid(),
  code: z.string(),
  discount_type: z.string(),
  discount_value: z.number(),
  used_count: z.number(),
  max_uses: z.number().nullable(),
});

export async function fetchPromoCodes(): Promise<z.infer<typeof promoSchema>[]> {
  const res = await fetch(`${getApiBaseUrl()}/api/v1/super-admin/promo-codes`, { headers: authHeaders() });
  if (!res.ok) throw new Error(String(res.status));
  return z.array(promoSchema).parse(await res.json());
}

export async function createPromoCode(payload: {
  code: string;
  discount_type: "percent" | "fixed_idr";
  discount_value: number;
  valid_plans: string[];
}): Promise<void> {
  const res = await fetch(`${getApiBaseUrl()}/api/v1/super-admin/promo-codes`, {
    method: "POST",
    headers: { ...authHeaders(), "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });
  if (!res.ok) throw new Error(await res.text());
}

export async function fetchPlatformSettings(): Promise<{ sections: Record<string, Record<string, unknown>> }> {
  const res = await fetch(`${getApiBaseUrl()}/api/v1/super-admin/platform-settings`, { headers: authHeaders() });
  if (!res.ok) throw new Error(String(res.status));
  return z.object({ sections: z.record(z.string(), z.record(z.string(), z.unknown())) }).parse(await res.json());
}

export async function updatePlatformSettings(
  sectionPatch: Record<string, Record<string, unknown>>,
): Promise<void> {
  const res = await fetch(`${getApiBaseUrl()}/api/v1/super-admin/platform-settings`, {
    method: "PUT",
    headers: { ...authHeaders(), "Content-Type": "application/json" },
    body: JSON.stringify({ sections: sectionPatch }),
  });
  if (!res.ok) throw new Error(await res.text());
}

const flagSchema = z.object({
  id: z.string().uuid(),
  name: z.string(),
  description: z.string(),
  enabled_global: z.boolean(),
  rollout_percent: z.number(),
});

export type FeatureFlag = z.infer<typeof flagSchema>;

export async function fetchFeatureFlags(): Promise<FeatureFlag[]> {
  const res = await fetch(`${getApiBaseUrl()}/api/v1/super-admin/feature-flags`, { headers: authHeaders() });
  if (!res.ok) throw new Error(String(res.status));
  return z.array(flagSchema).parse(await res.json());
}

export async function updateFeatureFlag(
  id: string,
  payload: { enabled_global?: boolean; rollout_percent?: number },
): Promise<void> {
  const res = await fetch(`${getApiBaseUrl()}/api/v1/super-admin/feature-flags/${id}`, {
    method: "PUT",
    headers: { ...authHeaders(), "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });
  if (!res.ok) throw new Error(await res.text());
}

const watchSchema = z.object({
  tenant_id: z.string().uuid(),
  tenant_name: z.string(),
  reason: z.string(),
  severity: z.string(),
});

export async function fetchWatchList(): Promise<z.infer<typeof watchSchema>[]> {
  const res = await fetch(`${getApiBaseUrl()}/api/v1/super-admin/watch-list`, { headers: authHeaders() });
  if (!res.ok) throw new Error(String(res.status));
  return z.array(watchSchema).parse(await res.json());
}

export async function downloadFinanceExport(): Promise<void> {
  const res = await fetch(`${getApiBaseUrl()}/api/v1/super-admin/finance/export?format=csv`, { headers: authHeaders() });
  if (!res.ok) throw new Error(String(res.status));
  const blob = await res.blob();
  const url = URL.createObjectURL(blob);
  const a = document.createElement("a");
  a.href = url;
  a.download = "finance-export.csv";
  a.click();
  URL.revokeObjectURL(url);
}

export async function impersonateTenant(tenantId: string): Promise<string> {
  const res = await fetch(`${getApiBaseUrl()}/api/v1/super-admin/tenants/${tenantId}/impersonate`, {
    method: "POST",
    headers: authHeaders(),
  });
  if (!res.ok) throw new Error(await res.text());
  const body = z.object({ access_token: z.string() }).parse(await res.json());
  return body.access_token;
}
