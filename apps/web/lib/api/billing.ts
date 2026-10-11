import { z } from "zod";

import { getApiBaseUrl } from "@/lib/auth/api";
import { ACCESS_TOKEN_COOKIE } from "@/lib/auth/constants";

function bearer(): string {
  const prefix = `${ACCESS_TOKEN_COOKIE}=`;
  const match = document.cookie.split(";").map((c) => c.trim()).find((c) => c.startsWith(prefix));
  const token = match ? decodeURIComponent(match.slice(prefix.length)) : null;
  if (!token) throw new Error("Belum masuk");
  return token;
}

const subscriptionSchema = z.object({
  plan_code: z.string(),
  plan_name: z.string(),
  status: z.string(),
  trial_ends_at: z.string().nullable(),
});

const usageSchema = z.object({
  devices_used: z.number(),
  devices_limit: z.number().nullable(),
  messages_used: z.number(),
  messages_limit: z.number().nullable(),
});

export async function fetchBillingSubscription() {
  const res = await fetch(`${getApiBaseUrl()}/api/v1/billing/subscription`, {
    headers: { Authorization: `Bearer ${bearer()}` },
  });
  if (!res.ok) throw new Error(String(res.status));
  return subscriptionSchema.parse(await res.json());
}

export async function fetchBillingUsage() {
  const res = await fetch(`${getApiBaseUrl()}/api/v1/billing/usage`, {
    headers: { Authorization: `Bearer ${bearer()}` },
  });
  if (!res.ok) throw new Error(String(res.status));
  return usageSchema.parse(await res.json());
}
