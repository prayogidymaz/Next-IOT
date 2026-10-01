import { z } from "zod";

export const automationPipelineRecordSchema = z.object({
  id: z.string(),
  tenant_id: z.string(),
  name: z.string(),
  description: z.string().nullable(),
  is_active: z.boolean(),
  nodes_json: z.array(z.record(z.string(), z.unknown())),
  edges_json: z.array(z.record(z.string(), z.unknown())),
  created_at: z.string(),
  updated_at: z.string(),
});
