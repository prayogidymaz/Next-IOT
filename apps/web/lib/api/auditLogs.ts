import { z } from "zod";

import { apiFetch, apiUrl } from "@/src/lib/api/client";

const auditLogItemSchema = z.object({
  id: z.string().uuid(),
  timestamp: z.string(),
  actor_id: z.string().uuid().nullable(),
  actor_email: z.string(),
  tenant_id: z.string().uuid().nullable(),
  action: z.string(),
  resource_target: z.string(),
  ip_address: z.string().nullable(),
  status: z.string(),
});

const auditLogListSchema = z.object({
  items: z.array(auditLogItemSchema),
  total: z.number(),
  page: z.number(),
  page_size: z.number(),
});

export type AuditLogItem = z.infer<typeof auditLogItemSchema>;
export type AuditLogList = z.infer<typeof auditLogListSchema>;

export type AuditLogQuery = {
  action?: string;
  actor?: string;
  start_time?: string;
  end_time?: string;
  page?: number;
  page_size?: number;
};

function queryString(params: AuditLogQuery): string {
  const q = new URLSearchParams();
  if (params.action && params.action !== "all") q.set("action", params.action);
  if (params.actor?.trim()) q.set("actor", params.actor.trim());
  if (params.start_time) q.set("start_time", params.start_time);
  if (params.end_time) q.set("end_time", params.end_time);
  q.set("page", String(params.page ?? 1));
  q.set("page_size", String(params.page_size ?? 50));
  return q.toString();
}

export async function fetchAuditLogs(params: AuditLogQuery): Promise<AuditLogList> {
  const res = await apiFetch(apiUrl(`/api/v1/audit-logs?${queryString(params)}`));
  if (!res.ok) {
    throw new Error(`Audit logs failed (${res.status})`);
  }
  return auditLogListSchema.parse(await res.json());
}

export async function downloadAuditLogsCsv(params: Omit<AuditLogQuery, "page" | "page_size">): Promise<void> {
  const q = new URLSearchParams();
  if (params.action && params.action !== "all") q.set("action", params.action);
  if (params.actor?.trim()) q.set("actor", params.actor.trim());
  if (params.start_time) q.set("start_time", params.start_time);
  if (params.end_time) q.set("end_time", params.end_time);
  const res = await apiFetch(apiUrl(`/api/v1/audit-logs/export?${q.toString()}`));
  if (!res.ok) {
    throw new Error(`Export failed (${res.status})`);
  }
  const blob = await res.blob();
  const url = URL.createObjectURL(blob);
  const a = document.createElement("a");
  a.href = url;
  a.download = `audit_logs_${new Date().toISOString().slice(0, 10)}.csv`;
  a.click();
  URL.revokeObjectURL(url);
}

export function parseResourceTarget(target: string): { type: string; id: string } {
  const idx = target.indexOf(":");
  if (idx === -1) return { type: target || "—", id: "—" };
  return { type: target.slice(0, idx), id: target.slice(idx + 1) || "—" };
}
