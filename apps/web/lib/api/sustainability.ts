import { z } from "zod";

import { getApiBaseUrl } from "@/lib/auth/api";
import { apiErrorMessage, jsonAuthHeaders } from "@/lib/auth/api-headers";

const carbonPointSchema = z.object({
  recorded_at: z.string(),
  co2_equivalent_kg: z.union([z.string(), z.number()]),
  source_type: z.string(),
});

const waterPointSchema = z.object({
  plot_id: z.string().uuid().nullable(),
  liters_used: z.union([z.string(), z.number()]),
  source: z.string(),
  recorded_at: z.string(),
});

const esgSchema = z.object({
  id: z.string().uuid(),
  period_month: z.string(),
  environmental_score: z.union([z.string(), z.number()]),
  social_score: z.union([z.string(), z.number()]),
  governance_score: z.union([z.string(), z.number()]),
  overall_grade: z.string(),
  generated_at: z.string(),
  report_pdf_url: z.string().nullable(),
});

export type CarbonPoint = z.infer<typeof carbonPointSchema>;
export type WaterPoint = z.infer<typeof waterPointSchema>;
export type EsgScorecard = z.infer<typeof esgSchema>;

export async function fetchCarbonTrend(from?: string, to?: string): Promise<CarbonPoint[]> {
  const q = new URLSearchParams();
  if (from) q.set("from", from);
  if (to) q.set("to", to);
  const res = await fetch(`${getApiBaseUrl()}/api/v1/sustainability/carbon?${q}`, { headers: jsonAuthHeaders() });
  if (!res.ok) throw new Error(await apiErrorMessage(res));
  return z.array(carbonPointSchema).parse(await res.json());
}

export async function fetchWaterUsage(): Promise<WaterPoint[]> {
  const res = await fetch(`${getApiBaseUrl()}/api/v1/sustainability/water`, { headers: jsonAuthHeaders() });
  if (!res.ok) throw new Error(await apiErrorMessage(res));
  return z.array(waterPointSchema).parse(await res.json());
}

export async function fetchCurrentEsg(): Promise<EsgScorecard | null> {
  const res = await fetch(`${getApiBaseUrl()}/api/v1/sustainability/esg/current`, { headers: jsonAuthHeaders() });
  if (!res.ok) throw new Error(await apiErrorMessage(res));
  const body: unknown = await res.json();
  if (body === null) return null;
  return esgSchema.parse(body);
}

export async function generateEsg(month: string): Promise<EsgScorecard> {
  const res = await fetch(`${getApiBaseUrl()}/api/v1/sustainability/esg/generate?month=${encodeURIComponent(month)}`, {
    method: "POST",
    headers: jsonAuthHeaders(),
  });
  if (!res.ok) throw new Error(await apiErrorMessage(res));
  return esgSchema.parse(await res.json());
}

export function esgPdfUrl(scorecardId: string): string {
  return `${getApiBaseUrl()}/api/v1/sustainability/esg/${scorecardId}/pdf`;
}
