import { z } from "zod";

import { apiFetch, apiUrl } from "@/src/lib/api/client";

const yieldForecastSchema = z.object({
  plot_id: z.string().uuid(),
  horizon_days: z.number(),
  estimated_kg: z.number(),
  confidence_interval: z.tuple([z.number(), z.number()]),
  risk_factors: z.array(z.string()),
  model_version: z.string(),
  forecast_date: z.string(),
});

export type YieldForecastResult = z.infer<typeof yieldForecastSchema>;

export async function fetchYieldForecast(plotId: string, horizonDays: number): Promise<YieldForecastResult> {
  const params = new URLSearchParams({
    plot_id: plotId,
    horizon_days: String(horizonDays),
  });
  const res = await apiFetch(apiUrl(`/api/v1/analytics/yield/forecast?${params.toString()}`));
  if (!res.ok) {
    throw new Error(`Yield forecast failed (${res.status})`);
  }
  return yieldForecastSchema.parse(await res.json());
}
