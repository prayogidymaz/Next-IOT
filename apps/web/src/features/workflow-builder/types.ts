import { z } from "zod";

export const workflowDraftTriggerSchema = z.object({
  kind: z.enum(["sensor_threshold", "cron", "event"]),
  sensor: z.string().optional(),
  operator: z.enum(["lt", "lte", "gt", "gte", "eq"]).optional(),
  threshold: z.number().optional(),
  device: z.string().optional(),
  cron: z.string().optional(),
  event_type: z.string().optional(),
  domain: z.string().optional(),
});

export const workflowDraftActionSchema = z.object({
  actuator: z.string().optional(),
  action: z.string(),
  duration_minutes: z.number().optional(),
  channels: z.array(z.string()).optional(),
  template: z.string().optional(),
  webhook_url: z.string().optional(),
});

export const workflowDraftSchema = z.object({
  draft_id: z.string().uuid(),
  tenant_id: z.string().uuid(),
  locale: z.string(),
  name: z.string(),
  description: z.string(),
  trigger: workflowDraftTriggerSchema,
  actions: z.array(workflowDraftActionSchema),
  confidence: z.number(),
  source: z.string(),
});

export type WorkflowDraft = z.infer<typeof workflowDraftSchema>;

export type WorkflowNodeKind = "trigger" | "condition" | "action";

export type WorkflowNodeData = {
  kind: WorkflowNodeKind;
  label: string;
  triggerKind?: "sensor_threshold" | "cron" | "event";
  sensor?: string;
  operator?: string;
  threshold?: number;
  cron?: string;
  logic?: "and" | "or" | "not";
  action?: string;
  actuator?: string;
  duration_minutes?: number;
};
