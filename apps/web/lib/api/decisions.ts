import { z } from "zod";

import { apiFetch, apiUrl } from "@/src/lib/api/client";

const recommendationSchema = z.object({
  id: z.string().uuid(),
  recommendation_type: z.string(),
  confidence: z.number(),
  status: z.string(),
  context_json: z.record(z.string(), z.unknown()),
});

export type DecisionRecommendation = z.infer<typeof recommendationSchema>;

const policySchema = z.object({
  id: z.string().uuid(),
  trigger_type: z.string(),
  min_confidence: z.number(),
  auto_apply: z.boolean(),
  approval_required: z.boolean(),
});

export type AutoActionPolicy = z.infer<typeof policySchema>;

export async function listDecisionRecommendations(): Promise<DecisionRecommendation[]> {
  const res = await apiFetch(apiUrl("/api/v1/decisions/recommendations"));
  if (!res.ok) throw new Error(`Decisions list failed (${res.status})`);
  return z.array(recommendationSchema).parse(await res.json());
}

export async function acceptRecommendation(id: string): Promise<DecisionRecommendation> {
  const res = await apiFetch(apiUrl(`/api/v1/decisions/recommendations/${id}/accept`), { method: "POST" });
  if (!res.ok) throw new Error(`Accept failed (${res.status})`);
  return recommendationSchema.parse(await res.json());
}

export async function rejectRecommendation(id: string): Promise<DecisionRecommendation> {
  const res = await apiFetch(apiUrl(`/api/v1/decisions/recommendations/${id}/reject`), { method: "POST" });
  if (!res.ok) throw new Error(`Reject failed (${res.status})`);
  return recommendationSchema.parse(await res.json());
}

export async function listAutoActionPolicies(): Promise<AutoActionPolicy[]> {
  const res = await apiFetch(apiUrl("/api/v1/decisions/policies"));
  if (!res.ok) throw new Error(`Policies list failed (${res.status})`);
  return z.array(policySchema).parse(await res.json());
}

export async function createAutoActionPolicy(body: {
  trigger_type: string;
  min_confidence: number;
  auto_apply: boolean;
  approval_required: boolean;
}): Promise<AutoActionPolicy> {
  const res = await apiFetch(apiUrl("/api/v1/decisions/policies"), { method: "POST", body: JSON.stringify(body) });
  if (!res.ok) throw new Error(`Create policy failed (${res.status})`);
  return policySchema.parse(await res.json());
}

export async function fetchOutcomeSummary(): Promise<Record<string, number>> {
  const res = await apiFetch(apiUrl("/api/v1/decisions/outcomes/summary"));
  if (!res.ok) throw new Error(`Outcomes failed (${res.status})`);
  return z.record(z.string(), z.number()).parse(await res.json());
}
