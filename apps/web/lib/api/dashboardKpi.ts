import { z } from "zod";

import { apiFetch, apiUrl } from "@/src/lib/api/client";

const kpiSchema = z.object({
  devices_online: z.number(),
  device_total: z.number(),
  messages_per_min: z.number(),
  active_alarms: z.number(),
  data_volume_today_gb: z.number(),
  devices_online_history: z.array(z.object({ hour: z.string(), online: z.number() })),
});

export type DashboardKpi = z.infer<typeof kpiSchema>;

export async function fetchDashboardKpi(): Promise<DashboardKpi> {
  const res = await apiFetch(apiUrl("/api/v1/dashboard/kpi"));
  if (!res.ok) throw new Error(`Dashboard KPI failed (${res.status})`);
  return kpiSchema.parse(await res.json());
}
