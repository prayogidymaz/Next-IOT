import { getApiBaseUrl } from "@/lib/auth/api";

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

function authHeaders(): HeadersInit {
  const token = typeof window !== "undefined" ? localStorage.getItem("access_token") ?? "" : "";
  return { Accept: "application/json", "Content-Type": "application/json", Authorization: `Bearer ${token}` };
}

export async function fetchWorkflowVersions(workflowId: string): Promise<WorkflowVersionRecord[]> {
  const res = await fetch(`${getApiBaseUrl()}/api/v1/workflows/${workflowId}/versions`, { headers: authHeaders() });
  if (!res.ok) throw new Error(await res.text());
  return res.json() as Promise<WorkflowVersionRecord[]>;
}

export async function rollbackWorkflowVersion(workflowId: string, versionNumber: number): Promise<void> {
  const res = await fetch(`${getApiBaseUrl()}/api/v1/workflows/${workflowId}/versions/${versionNumber}/rollback`, {
    method: "POST",
    headers: authHeaders(),
  });
  if (!res.ok) throw new Error(await res.text());
}

export async function fetchVersionDiff(
  workflowId: string,
  versionAId: string,
  versionBId: string,
): Promise<VersionDiff> {
  const res = await fetch(
    `${getApiBaseUrl()}/api/v1/workflows/${workflowId}/versions/${versionAId}/diff/${versionBId}`,
    { headers: authHeaders() },
  );
  if (!res.ok) throw new Error(await res.text());
  return res.json() as Promise<VersionDiff>;
}
