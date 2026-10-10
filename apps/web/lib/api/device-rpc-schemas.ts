import { z } from "zod";

export const deviceRpcItemSchema = z.object({
  id: z.string(),
  method: z.string(),
  params: z.record(z.string(), z.unknown()),
  status: z.string(),
  response_json: z.unknown().nullable(),
  error_message: z.string().nullable(),
  timeout_seconds: z.number(),
  requested_at: z.string(),
  delivered_at: z.string().nullable(),
  completed_at: z.string().nullable(),
});

export const deviceRpcListSchema = z.object({
  items: z.array(deviceRpcItemSchema),
});

export const deviceRpcCreateResponseSchema = z.object({
  status: z.string(),
  response: z.unknown().optional(),
  reason: z.string().optional(),
  request_id: z.string().nullable().optional(),
});

export type DeviceRpcItem = z.infer<typeof deviceRpcItemSchema>;
