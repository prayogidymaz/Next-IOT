import { getApiBaseUrl } from "@/lib/auth/api";
import { apiErrorMessage, jsonAuthHeaders } from "@/lib/auth/api-headers";

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

const DEFAULT_POLICY: Omit<ApprovalPolicy, "tenant_id"> = {
  require_approval_for_production: false,
  min_approvers: 1,
  approver_roles_json: ["tenant_admin", "operator"],
};

export async function requestWorkflowApproval(workflowId: string, notes: string): Promise<ApprovalRequestRecord> {
  const res = await fetch(`${getApiBaseUrl()}/api/v1/workflows/${workflowId}/approval/request`, {
    method: "POST",
    headers: jsonAuthHeaders(),
    body: JSON.stringify({ notes }),
  });
  if (!res.ok) throw new Error(await apiErrorMessage(res));
  return res.json() as Promise<ApprovalRequestRecord>;
}

export async function fetchPendingApprovals(): Promise<ApprovalRequestRecord[]> {
  const res = await fetch(`${getApiBaseUrl()}/api/v1/approval/pending`, { headers: jsonAuthHeaders(false) });
  if (res.status === 401) return [];
  if (!res.ok) throw new Error(await apiErrorMessage(res));
  return res.json() as Promise<ApprovalRequestRecord[]>;
}

export async function approveRequest(requestId: string, notes: string): Promise<void> {
  const res = await fetch(`${getApiBaseUrl()}/api/v1/approval/${requestId}/approve`, {
    method: "POST",
    headers: jsonAuthHeaders(),
    body: JSON.stringify({ notes }),
  });
  if (!res.ok) throw new Error(await apiErrorMessage(res));
}

export async function rejectRequest(requestId: string, notes: string): Promise<void> {
  const res = await fetch(`${getApiBaseUrl()}/api/v1/approval/${requestId}/reject`, {
    method: "POST",
    headers: jsonAuthHeaders(),
    body: JSON.stringify({ notes }),
  });
  if (!res.ok) throw new Error(await apiErrorMessage(res));
}

export async function fetchApprovalPolicy(): Promise<ApprovalPolicy> {
  const res = await fetch(`${getApiBaseUrl()}/api/v1/approval/policy`, { headers: jsonAuthHeaders(false) });
  if (res.status === 401) {
    return { tenant_id: "", ...DEFAULT_POLICY };
  }
  if (!res.ok) throw new Error(await apiErrorMessage(res));
  return res.json() as Promise<ApprovalPolicy>;
}

export async function updateApprovalPolicy(policy: Omit<ApprovalPolicy, "tenant_id">): Promise<ApprovalPolicy> {
  const res = await fetch(`${getApiBaseUrl()}/api/v1/approval/policy`, {
    method: "PUT",
    headers: jsonAuthHeaders(),
    body: JSON.stringify(policy),
  });
  if (!res.ok) throw new Error(await apiErrorMessage(res));
  return res.json() as Promise<ApprovalPolicy>;
}
