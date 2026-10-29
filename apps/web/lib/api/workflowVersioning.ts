import { getApiBaseUrl } from "@/lib/auth/api";
import { apiErrorMessage, jsonAuthHeaders } from "@/lib/auth/api-headers";

export type WorkflowVersionRecord = {
  id: string;
  workflow_id: string;
  version_number: number;
  snapshot_json: Record<string, unknown>;
  created_by: string | null;
  created_at: string;
  is_active: boolean;
  parent_version_id: string | null;
};

export type VersionDiff = {
  added_nodes: string[];
  removed_nodes: string[];
  modified_nodes: string[];
  added_edges: string[];
  removed_edges: string[];
};

export async function fetchWorkflowVersions(workflowId: string): Promise<WorkflowVersionRecord[]> {
  const res = await fetch(`${getApiBaseUrl()}/api/v1/workflows/${workflowId}/versions`, {
    headers: jsonAuthHeaders(false),
  });
  if (res.status === 401) return [];
  if (!res.ok) throw new Error(await apiErrorMessage(res));
  return res.json() as Promise<WorkflowVersionRecord[]>;
}

export async function rollbackWorkflowVersion(workflowId: string, versionNumber: number): Promise<void> {
  const res = await fetch(`${getApiBaseUrl()}/api/v1/workflows/${workflowId}/versions/${versionNumber}/rollback`, {
    method: "POST",
    headers: jsonAuthHeaders(false),
  });
  if (!res.ok) throw new Error(await apiErrorMessage(res));
}

export async function fetchVersionDiff(
  workflowId: string,
  versionAId: string,
  versionBId: string,
): Promise<VersionDiff> {
  const res = await fetch(
    `${getApiBaseUrl()}/api/v1/workflows/${workflowId}/versions/${versionAId}/diff/${versionBId}`,
    { headers: jsonAuthHeaders(false) },
  );
  if (!res.ok) throw new Error(await apiErrorMessage(res));
  return res.json() as Promise<VersionDiff>;
}
