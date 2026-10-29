import { getApiBaseUrl } from "@/lib/auth/api";

export type ApprovalRequestRecord = {
  id: string;
  workflow_id: string;
  requested_by: string;
  requested_at: string;
  status: string;
  notes: string;
  approved_by: string | null;
  approved_at: string | null;
  approval_notes: string | null;
};

export type ApprovalPolicy = {
  tenant_id: string;
  require_approval_for_production: boolean;
  min_approvers: number;
  approver_roles_json: string[];
};

function authHeaders(): HeadersInit {
  const token = typeof window !== "undefined" ? localStorage.getItem("access_token") ?? "" : "";
  return { Accept: "application/json", "Content-Type": "application/json", Authorization: `Bearer ${token}` };
}

export async function requestWorkflowApproval(workflowId: string, notes: string): Promise<ApprovalRequestRecord> {
  const res = await fetch(`${getApiBaseUrl()}/api/v1/workflows/${workflowId}/approval/request`, {
    method: "POST",
    headers: authHeaders(),
    body: JSON.stringify({ notes }),
  });
  if (!res.ok) throw new Error(await res.text());
  return res.json() as Promise<ApprovalRequestRecord>;
}

export async function fetchPendingApprovals(): Promise<ApprovalRequestRecord[]> {
  const res = await fetch(`${getApiBaseUrl()}/api/v1/approval/pending`, { headers: authHeaders() });
  if (!res.ok) throw new Error(await res.text());
  return res.json() as Promise<ApprovalRequestRecord[]>;
}

export async function approveRequest(requestId: string, notes: string): Promise<void> {
  const res = await fetch(`${getApiBaseUrl()}/api/v1/approval/${requestId}/approve`, {
    method: "POST",
    headers: authHeaders(),
    body: JSON.stringify({ notes }),
  });
  if (!res.ok) throw new Error(await res.text());
}

export async function rejectRequest(requestId: string, notes: string): Promise<void> {
  const res = await fetch(`${getApiBaseUrl()}/api/v1/approval/${requestId}/reject`, {
    method: "POST",
    headers: authHeaders(),
    body: JSON.stringify({ notes }),
  });
  if (!res.ok) throw new Error(await res.text());
}

export async function fetchApprovalPolicy(): Promise<ApprovalPolicy> {
  const res = await fetch(`${getApiBaseUrl()}/api/v1/approval/policy`, { headers: authHeaders() });
  if (!res.ok) throw new Error(await res.text());
  return res.json() as Promise<ApprovalPolicy>;
}

export async function updateApprovalPolicy(policy: Omit<ApprovalPolicy, "tenant_id">): Promise<ApprovalPolicy> {
  const res = await fetch(`${getApiBaseUrl()}/api/v1/approval/policy`, {
    method: "PUT",
    headers: authHeaders(),
    body: JSON.stringify(policy),
  });
  if (!res.ok) throw new Error(await res.text());
  return res.json() as Promise<ApprovalPolicy>;
}
