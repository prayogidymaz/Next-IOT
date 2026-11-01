import { z } from "zod";

import { getApiBaseUrl } from "@/lib/auth/api";
import { apiErrorMessage, jsonAuthHeaders } from "@/lib/auth/api-headers";

const siteSchema = z.object({
  id: z.string().uuid(),
  tenant_id: z.string().uuid(),
  name: z.string(),
  slug: z.string(),
  parent_site_id: z.string().uuid().nullable(),
  location_json: z.record(z.unknown()),
  timezone: z.string(),
  is_active: z.boolean(),
  created_at: z.string(),
});

const plotSchema = z.object({
  id: z.string().uuid(),
  site_id: z.string().uuid(),
  name: z.string(),
  crop_type: z.string(),
  area_hectares: z.union([z.string(), z.number()]),
  soil_type: z.string(),
  planting_date: z.string().nullable(),
  expected_harvest_date: z.string().nullable(),
  metadata_json: z.record(z.unknown()),
  is_active: z.boolean(),
  created_at: z.string(),
});

const reportSchema = z.object({
  site_id: z.string().uuid(),
  period_days: z.number(),
  plot_count: z.number(),
  total_area_hectares: z.number(),
  active_plots: z.number(),
});

export type SiteRecord = z.infer<typeof siteSchema>;
export type PlotRecord = z.infer<typeof plotSchema>;
export type SiteReport = z.infer<typeof reportSchema>;

export async function createSite(body: {
  name: string;
  slug: string;
  timezone: string;
  location_json: Record<string, unknown>;
}): Promise<SiteRecord> {
  const res = await fetch(`${getApiBaseUrl()}/api/v1/sites`, {
    method: "POST",
    headers: jsonAuthHeaders(),
    body: JSON.stringify(body),
  });
  if (!res.ok) throw new Error(await apiErrorMessage(res));
  return siteSchema.parse(await res.json());
}

export async function listSites(): Promise<SiteRecord[]> {
  const res = await fetch(`${getApiBaseUrl()}/api/v1/sites`, { headers: jsonAuthHeaders() });
  if (!res.ok) throw new Error(await apiErrorMessage(res));
  return z.array(siteSchema).parse(await res.json());
}

export async function getSite(siteId: string): Promise<SiteRecord> {
  const res = await fetch(`${getApiBaseUrl()}/api/v1/sites/${siteId}`, { headers: jsonAuthHeaders() });
  if (!res.ok) throw new Error(await apiErrorMessage(res));
  return siteSchema.parse(await res.json());
}

export async function listSitePlots(siteId: string): Promise<PlotRecord[]> {
  const res = await fetch(`${getApiBaseUrl()}/api/v1/sites/${siteId}/plots`, { headers: jsonAuthHeaders() });
  if (!res.ok) throw new Error(await apiErrorMessage(res));
  return z.array(plotSchema).parse(await res.json());
}

export async function getSiteReport(siteId: string, period = 30): Promise<SiteReport> {
  const res = await fetch(`${getApiBaseUrl()}/api/v1/sites/${siteId}/report?period=${period}`, {
    headers: jsonAuthHeaders(),
  });
  if (!res.ok) throw new Error(await apiErrorMessage(res));
  return reportSchema.parse(await res.json());
}
