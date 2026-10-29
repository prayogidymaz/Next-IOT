import { getApiBaseUrl } from "@/lib/auth/api";

export type WorkflowTemplateRecord = {
  id: string;
  name: string;
  description: string;
  category: string;
  tags_json: string[];
  author_tenant_id: string;
  snapshot_json: Record<string, unknown>;
  downloads_count: number;
  rating_avg: number;
  rating_count: number;
  published: boolean;
  created_at: string;
  locale: string;
};

function authHeaders(): HeadersInit {
  const token = typeof window !== "undefined" ? localStorage.getItem("access_token") ?? "" : "";
  return { Accept: "application/json", "Content-Type": "application/json", Authorization: `Bearer ${token}` };
}

export async function listMarketplaceTemplates(params: {
  category?: string;
  locale?: string;
  sort?: string;
  limit?: number;
}): Promise<WorkflowTemplateRecord[]> {
  const q = new URLSearchParams();
  if (params.category) q.set("category", params.category);
  if (params.locale) q.set("locale", params.locale);
  if (params.sort) q.set("sort", params.sort);
  if (params.limit) q.set("limit", String(params.limit));
  const res = await fetch(`${getApiBaseUrl()}/api/v1/marketplace/templates?${q.toString()}`, {
    headers: authHeaders(),
  });
  if (!res.ok) throw new Error(await res.text());
  return res.json() as Promise<WorkflowTemplateRecord[]>;
}

export async function getMarketplaceTemplate(templateId: string): Promise<WorkflowTemplateRecord> {
  const res = await fetch(`${getApiBaseUrl()}/api/v1/marketplace/templates/${templateId}`, { headers: authHeaders() });
  if (!res.ok) throw new Error(await res.text());
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
    headers: authHeaders(),
    body: JSON.stringify(body),
  });
  if (!res.ok) throw new Error(await res.text());
  return res.json() as Promise<WorkflowTemplateRecord>;
}

export async function downloadMarketplaceTemplate(templateId: string): Promise<{ id: string }> {
  const res = await fetch(`${getApiBaseUrl()}/api/v1/marketplace/templates/${templateId}/download`, {
    method: "POST",
    headers: authHeaders(),
    body: JSON.stringify({}),
  });
  if (!res.ok) throw new Error(await res.text());
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
    headers: authHeaders(),
    body: JSON.stringify({ rating, review }),
  });
  if (!res.ok) throw new Error(await res.text());
}

export async function unpublishMarketplaceTemplate(templateId: string): Promise<void> {
  const res = await fetch(`${getApiBaseUrl()}/api/v1/marketplace/templates/${templateId}`, {
    method: "DELETE",
    headers: authHeaders(),
  });
  if (!res.ok) throw new Error(await res.text());
}
