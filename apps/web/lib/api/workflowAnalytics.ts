import { getApiBaseUrl } from "@/lib/auth/api";

export type WorkflowStatsRecord = {
  workflow_id: string;
  name: string;
  fire_count: number;
  success_count: number;
  fail_count: number;
  avg_duration_ms: number;
  savings_idr_estimate: number;
};

export type TimelinePoint = {
  date: string;
  fire_count: number;
  success_count: number;
};

export type SavingsReport = {
  water_liters_saved: number;
  kwh_saved: number;
  idr_total: number;
  calculation_breakdown: Record<string, unknown>;
};

export type FailureReport = {
  common_errors: string[];
  failed_at_step: string | null;
  suggested_fix: string;
  failure_rate: number;
};

function authHeaders(): HeadersInit {
  const token = typeof window !== "undefined" ? localStorage.getItem("access_token") ?? "" : "";
  return { Accept: "application/json", Authorization: `Bearer ${token}` };
}

export async function fetchTopFiredWorkflows(periodDays: number): Promise<WorkflowStatsRecord[]> {
  const res = await fetch(`${getApiBaseUrl()}/api/v1/analytics/workflows/top-fired?period_days=${periodDays}`, {
    headers: authHeaders(),
  });
  if (!res.ok) throw new Error(await res.text());
  return res.json() as Promise<WorkflowStatsRecord[]>;
}

export async function fetchWorkflowTimeline(workflowId: string, periodDays: number): Promise<{ points: TimelinePoint[] }> {
  const res = await fetch(
    `${getApiBaseUrl()}/api/v1/analytics/workflows/${workflowId}/timeline?period_days=${periodDays}`,
    { headers: authHeaders() },
  );
  if (!res.ok) throw new Error(await res.text());
  return res.json() as Promise<{ points: TimelinePoint[] }>;
}

export async function fetchWorkflowSavings(workflowId: string): Promise<SavingsReport> {
  const res = await fetch(`${getApiBaseUrl()}/api/v1/analytics/workflows/${workflowId}/savings`, {
    headers: authHeaders(),
  });
  if (!res.ok) throw new Error(await res.text());
  return res.json() as Promise<SavingsReport>;
}

export async function fetchWorkflowFailures(workflowId: string): Promise<FailureReport> {
  const res = await fetch(`${getApiBaseUrl()}/api/v1/analytics/workflows/${workflowId}/failures`, {
    headers: authHeaders(),
  });
  if (!res.ok) throw new Error(await res.text());
  return res.json() as Promise<FailureReport>;
}
