import { z } from "zod";

export const meshDomainSchema = z.enum([
  "sensor",
  "vision",
  "motion",
  "actuator",
  "security",
  "ui",
]);

export const meshContextSchema = z.object({
  farm_id: z.string().uuid().nullable().optional(),
  plot_id: z.string().uuid().nullable().optional(),
  geo_location: z
    .object({
      lat: z.number(),
      lng: z.number(),
    })
    .nullable()
    .optional(),
  physical_zone: z.string().nullable().optional(),
  capabilities: z.array(z.string()).optional(),
});

export const meshEventSchema = z.object({
  event_id: z.string().uuid(),
  tenant_id: z.string().uuid(),
  device_id: z.string().uuid(),
  domain: meshDomainSchema,
  event_type: z.string(),
  timestamp: z.string(),
  payload: z.record(z.unknown()),
  context: meshContextSchema,
  correlation_id: z.string().uuid().nullable(),
  parent_event_id: z.string().uuid().nullable(),
  created_at: z.string().optional(),
});

export type MeshEventRecord = z.infer<typeof meshEventSchema>;

export const meshWorkflowTriggerSchema = z.object({
  type: z.enum(["mesh_event", "schedule", "manual"]),
  filter: z
    .object({
      domain: z.string().nullable().optional(),
      event_type: z.string().nullable().optional(),
    })
    .nullable()
    .optional(),
});

export const meshWorkflowDefinitionSchema = z.object({
  name: z.string(),
  description: z.string().optional(),
  enabled: z.boolean().optional(),
  trigger: meshWorkflowTriggerSchema,
  conditions: z.array(z.record(z.unknown())).optional(),
  actions: z.array(z.record(z.unknown())),
});

export const meshWorkflowRecordSchema = z.object({
  id: z.string().uuid(),
  tenant_id: z.string().uuid(),
  name: z.string(),
  description: z.string(),
  enabled: z.boolean(),
  definition: meshWorkflowDefinitionSchema,
  created_at: z.string(),
  updated_at: z.string(),
});

export type MeshWorkflowRecord = z.infer<typeof meshWorkflowRecordSchema>;

export const workflowDryRunResponseSchema = z.object({
  conditions_passed: z.boolean(),
  planned_actions: z.array(z.record(z.unknown())),
  skipped_reason: z.string().nullable(),
});

export const workflowExecutionSchema = z.object({
  id: z.string().uuid(),
  workflow_id: z.string().uuid(),
  tenant_id: z.string().uuid(),
  trigger_event_id: z.string().uuid().nullable(),
  status: z.string(),
  started_at: z.string(),
  completed_at: z.string().nullable(),
  duration_ms: z.number().nullable(),
  action_results: z.record(z.unknown()),
  error_message: z.string().nullable(),
  correlation_id: z.string().uuid().nullable(),
});
