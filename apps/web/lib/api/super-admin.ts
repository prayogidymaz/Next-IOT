import { z } from "zod";

import { getApiBaseUrl } from "@/lib/auth/api";
import { readAccessTokenFromDocument } from "@/lib/auth/token-role";

import {
  invoiceSchema,
  platformStatsSchema,
  revenueSchema,
  systemHealthSchema,
  tenantAdminItemSchema,
  tenantDetailSchema,
  type PlatformInvoice,
  type PlatformStats,
  type RevenueReport,
  type SystemHealth,
  type TenantAdminItem,
  type TenantDetail,
} from "./super-admin-schemas";

function authHeaders(): HeadersInit {
  const token = readAccessTokenFromDocument();
  if (!token) throw new Error("Belum masuk");
  return { Accept: "application/json", Authorization: `Bearer ${token}` };
}

export function formatIdr(value: number): string {
  return new Intl.NumberFormat("id-ID", { style: "currency", currency: "IDR", maximumFractionDigits: 0 }).format(
    value,
  );
}

export async function fetchSuperAdminStats(): Promise<PlatformStats> {
  const res = await fetch(`${getApiBaseUrl()}/api/v1/super-admin/stats`, { headers: authHeaders() });
  if (!res.ok) throw new Error(String(res.status));
  return platformStatsSchema.parse(await res.json());
}

export async function fetchSuperAdminRevenue(months = 12): Promise<RevenueReport> {
  const res = await fetch(`${getApiBaseUrl()}/api/v1/super-admin/revenue?months=${months}`, {
    headers: authHeaders(),
  });
  if (!res.ok) throw new Error(String(res.status));
  return revenueSchema.parse(await res.json());
}

export async function fetchSuperAdminTenants(params: {
  status?: string;
  plan?: string;
  q?: string;
}): Promise<TenantAdminItem[]> {
  const qs = new URLSearchParams();
  if (params.status) qs.set("status", params.status);
  if (params.plan) qs.set("plan", params.plan);
  if (params.q) qs.set("q", params.q);
  const suffix = qs.toString() ? `?${qs.toString()}` : "";
  const res = await fetch(`${getApiBaseUrl()}/api/v1/super-admin/tenants${suffix}`, { headers: authHeaders() });
  if (!res.ok) throw new Error(String(res.status));
  return z.array(tenantAdminItemSchema).parse(await res.json());
}

export async function fetchSuperAdminTenantDetail(tenantId: string): Promise<TenantDetail> {
  const res = await fetch(`${getApiBaseUrl()}/api/v1/super-admin/tenants/${tenantId}`, { headers: authHeaders() });
  if (!res.ok) throw new Error(String(res.status));
  return tenantDetailSchema.parse(await res.json());
}

export async function suspendTenant(tenantId: string, reason?: string): Promise<void> {
  const res = await fetch(`${getApiBaseUrl()}/api/v1/super-admin/tenants/${tenantId}/suspend`, {
    method: "POST",
    headers: { ...authHeaders(), "Content-Type": "application/json" },
    body: JSON.stringify(reason ? { reason } : {}),
  });
  if (!res.ok) throw new Error(await res.text());
}

export async function unsuspendTenant(tenantId: string): Promise<void> {
  const res = await fetch(`${getApiBaseUrl()}/api/v1/super-admin/tenants/${tenantId}/unsuspend`, {
    method: "POST",
    headers: authHeaders(),
  });
  if (!res.ok) throw new Error(await res.text());
}

export async function extendTenantTrial(tenantId: string, days: number): Promise<void> {
  const res = await fetch(`${getApiBaseUrl()}/api/v1/super-admin/tenants/${tenantId}/extend-trial`, {
    method: "POST",
    headers: { ...authHeaders(), "Content-Type": "application/json" },
    body: JSON.stringify({ days }),
  });
  if (!res.ok) throw new Error(await res.text());
}

export async function changeTenantPlan(tenantId: string, planCode: string, prorate: boolean): Promise<void> {
  const res = await fetch(`${getApiBaseUrl()}/api/v1/super-admin/tenants/${tenantId}/change-plan`, {
    method: "POST",
    headers: { ...authHeaders(), "Content-Type": "application/json" },
    body: JSON.stringify({ plan_code: planCode, prorate }),
  });
  if (!res.ok) throw new Error(await res.text());
}

export async function fetchSuperAdminInvoices(status?: string): Promise<PlatformInvoice[]> {
  const qs = status ? `?status=${encodeURIComponent(status)}` : "";
  const res = await fetch(`${getApiBaseUrl()}/api/v1/super-admin/invoices${qs}`, { headers: authHeaders() });
  if (!res.ok) throw new Error(String(res.status));
  return z.array(invoiceSchema).parse(await res.json());
}

export async function fetchSuperAdminSystemHealth(): Promise<SystemHealth> {
  const res = await fetch(`${getApiBaseUrl()}/api/v1/super-admin/system-health`, { headers: authHeaders() });
  if (!res.ok) throw new Error(String(res.status));
  return systemHealthSchema.parse(await res.json());
}

export type {
  PlatformInvoice,
  PlatformStats,
  RevenueReport,
  SystemHealth,
  TenantAdminItem,
  TenantDetail,
} from "./super-admin-schemas";

export async function runBillingCycle(): Promise<{ invoices_created: number; past_due_marked: number; expired_marked: number }> {
  const res = await fetch(`${getApiBaseUrl()}/api/v1/super-admin/billing-cycle/run`, {
    method: "POST",
    headers: authHeaders(),
  });
  if (!res.ok) throw new Error(await res.text());
  return z
    .object({
      invoices_created: z.number(),
      past_due_marked: z.number(),
      expired_marked: z.number(),
    })
    .parse(await res.json());
}
