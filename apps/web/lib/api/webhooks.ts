import { z } from "zod";

import { getApiBaseUrl } from "@/lib/auth/api";
import { apiErrorMessage, jsonAuthHeaders } from "@/lib/auth/api-headers";

const webhookSchema = z.object({
  id: z.string().uuid(),
  url: z.string(),
  event_types_json: z.array(z.string()),
  active: z.boolean(),
  last_delivery_at: z.string().nullable(),
  created_at: z.string(),
});

export type WebhookRecord = z.infer<typeof webhookSchema>;

export async function listWebhooks(): Promise<WebhookRecord[]> {
  const res = await fetch(`${getApiBaseUrl()}/api/v1/webhooks`, { headers: jsonAuthHeaders() });
  if (!res.ok) throw new Error(await apiErrorMessage(res));
  return z.array(webhookSchema).parse(await res.json());
}

export async function createWebhook(body: { url: string; event_types: string[]; secret_token: string }): Promise<WebhookRecord> {
  const res = await fetch(`${getApiBaseUrl()}/api/v1/webhooks`, {
    method: "POST",
    headers: jsonAuthHeaders(),
    body: JSON.stringify(body),
  });
  if (!res.ok) throw new Error(await apiErrorMessage(res));
  return webhookSchema.parse(await res.json());
}

export async function testWebhook(webhookId: string): Promise<{ delivered: boolean }> {
  const res = await fetch(`${getApiBaseUrl()}/api/v1/webhooks/${webhookId}/test`, {
    method: "POST",
    headers: jsonAuthHeaders(),
  });
  if (!res.ok) throw new Error(await apiErrorMessage(res));
  return z.object({ delivered: z.boolean() }).parse(await res.json());
}
