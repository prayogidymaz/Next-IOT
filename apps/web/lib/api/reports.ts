import { z } from "zod";

import { apiFetch, apiUrl } from "@/src/lib/api/client";

const templateSchema = z.object({
  id: z.string().uuid(),
  tenant_id: z.string().uuid(),
  name: z.string(),
  description: z.string(),
  config_json: z.record(z.string(), z.unknown()),
  is_public: z.boolean(),
  created_at: z.string(),
});

export type ReportTemplate = z.infer<typeof templateSchema>;

export async function listReportTemplates(): Promise<ReportTemplate[]> {
  const res = await apiFetch(apiUrl("/api/v1/reports/templates"));
  if (!res.ok) throw new Error(`Reports list failed (${res.status})`);
  return z.array(templateSchema).parse(await res.json());
}

export async function createReportTemplate(body: {
  name: string;
  description: string;
  config_json: Record<string, unknown>;
}): Promise<ReportTemplate> {
  const res = await apiFetch(apiUrl("/api/v1/reports/templates"), { method: "POST", body: JSON.stringify(body) });
  if (!res.ok) throw new Error(`Create report failed (${res.status})`);
  return templateSchema.parse(await res.json());
}
