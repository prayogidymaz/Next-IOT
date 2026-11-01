import { getApiBaseUrl } from "@/lib/auth/api";
import { apiErrorMessage, jsonAuthHeaders, publicJsonHeaders } from "@/lib/auth/api-headers";

export type WorkflowTemplateRecord = {
  id: string;
  name: string;
  description: string;
  category: string;
  tags_json: string[];
  author_tenant_id: string;
  author_tenant_name?: string;
  snapshot_json: Record<string, unknown>;
  downloads_count: number;
  rating_avg: number;
  rating_count: number;
  published: boolean;
  created_at: string;
  locale: string;
  price_idr?: number;
  author_user_id?: string | null;
};

export type CheckoutResult = {
  provider: string;
  amount_idr: number;
  checkout_url: string;
  payment_ref?: string | null;
};

export type SellerDashboard = {
  tier: string;
  lifetime_sales_idr: number;
  commission_rate_percent: number;
  verified_badge: boolean;
  pending_payout_idr: number;
};

export type SellerPayout = {
  id: string;
  period_month: string;
  gross_sales_idr: number;
  commission_idr: number;
  status: string;
  paid_at: string | null;
  transaction_ref: string | null;
};

export async function listMarketplaceTemplates(params: {
  category?: string;
  sort?: string;
  limit?: number;
  search?: string;
  locale?: string;
}): Promise<WorkflowTemplateRecord[]> {
  const q = new URLSearchParams();
  if (params.category) q.set("category", params.category);
  if (params.sort) q.set("sort", params.sort);
  if (params.limit) q.set("limit", String(params.limit));
  if (params.search) q.set("search", params.search);
  if (params.locale) q.set("locale", params.locale);
  const res = await fetch(`${getApiBaseUrl()}/api/v1/marketplace/templates?${q.toString()}`, {
    headers: publicJsonHeaders(),
  });
  if (!res.ok) throw new Error(await apiErrorMessage(res));
  return res.json() as Promise<WorkflowTemplateRecord[]>;
}

export async function getMarketplaceTemplate(templateId: string): Promise<WorkflowTemplateRecord> {
  const res = await fetch(`${getApiBaseUrl()}/api/v1/marketplace/templates/${templateId}`, {
    headers: publicJsonHeaders(),
  });
  if (!res.ok) throw new Error(await apiErrorMessage(res));
  return res.json() as Promise<WorkflowTemplateRecord>;
}

export async function publishWorkflowTemplate(body: {
  workflow_id: string;
  name: string;
  description: string;
  category: string;
  tags: string[];
  locale?: string;
}): Promise<WorkflowTemplateRecord> {
  const res = await fetch(`${getApiBaseUrl()}/api/v1/marketplace/publish`, {
    method: "POST",
    headers: jsonAuthHeaders(),
    body: JSON.stringify(body),
  });
  if (!res.ok) throw new Error(await apiErrorMessage(res));
  return res.json() as Promise<WorkflowTemplateRecord>;
}

export async function downloadMarketplaceTemplate(templateId: string): Promise<{ id: string }> {
  const res = await fetch(`${getApiBaseUrl()}/api/v1/marketplace/templates/${templateId}/download`, {
    method: "POST",
    headers: jsonAuthHeaders(),
    body: JSON.stringify({}),
  });
  if (!res.ok) throw new Error(await apiErrorMessage(res));
  const body = (await res.json()) as { id: string };
  return body;
}

export async function rateMarketplaceTemplate(
  templateId: string,
  rating: number,
  review: string,
): Promise<void> {
  const res = await fetch(`${getApiBaseUrl()}/api/v1/marketplace/templates/${templateId}/rate`, {
    method: "POST",
    headers: jsonAuthHeaders(),
    body: JSON.stringify({ rating, review }),
  });
  if (!res.ok) throw new Error(await apiErrorMessage(res));
}

export async function unpublishMarketplaceTemplate(templateId: string): Promise<void> {
  const res = await fetch(`${getApiBaseUrl()}/api/v1/marketplace/templates/${templateId}`, {
    method: "DELETE",
    headers: jsonAuthHeaders(false),
  });
  if (!res.ok) throw new Error(await apiErrorMessage(res));
}

export async function checkoutMarketplaceTemplate(templateId: string): Promise<CheckoutResult> {
  const res = await fetch(`${getApiBaseUrl()}/api/v1/marketplace/templates/${templateId}/checkout`, {
    method: "POST",
    headers: jsonAuthHeaders(),
  });
  if (!res.ok) throw new Error(await apiErrorMessage(res));
  return res.json() as Promise<CheckoutResult>;
}

export async function fetchSellerDashboard(): Promise<SellerDashboard> {
  const res = await fetch(`${getApiBaseUrl()}/api/v1/marketplace/seller/dashboard`, { headers: jsonAuthHeaders() });
  if (!res.ok) throw new Error(await apiErrorMessage(res));
  return res.json() as Promise<SellerDashboard>;
}

export async function fetchSellerPayouts(): Promise<SellerPayout[]> {
  const res = await fetch(`${getApiBaseUrl()}/api/v1/marketplace/seller/payouts`, { headers: jsonAuthHeaders() });
  if (!res.ok) throw new Error(await apiErrorMessage(res));
  return res.json() as Promise<SellerPayout[]>;
}

export function formatPriceIdr(price: number | undefined): string {
  const v = price ?? 0;
  if (v <= 0) return "Free";
  if (v >= 1_000_000) return `Rp ${(v / 1_000_000).toFixed(1)}jt`;
  if (v >= 1_000) return `Rp ${Math.round(v / 1000)}rb`;
  return `Rp ${v}`;
}
