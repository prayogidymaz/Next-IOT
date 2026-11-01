import { z } from "zod";

import { apiFetch, apiUrl } from "@/src/lib/api/client";

const workflowSchema = z.object({
  id: z.string().uuid(),
  tenant_id: z.string().uuid(),
  name: z.string(),
  description: z.string(),
  enabled: z.boolean(),
  created_at: z.string(),
  updated_at: z.string(),
  last_fired_at: z.string().nullable().optional(),
  success_rate_percent: z.number().optional(),
  action_count: z.number().optional(),
});

export type MeshWorkflowListItem = z.infer<typeof workflowSchema>;

export async function listMeshWorkflows(params?: { enabled?: boolean; search?: string }): Promise<MeshWorkflowListItem[]> {
  const q = new URLSearchParams();
  if (params?.enabled !== undefined) q.set("enabled", String(params.enabled));
  if (params?.search) q.set("search", params.search);
  const res = await apiFetch(apiUrl(`/api/v1/mesh/workflows?${q.toString()}`));
  if (!res.ok) throw new Error(`Workflow list failed (${res.status})`);
  return z.array(workflowSchema).parse(await res.json());
}
