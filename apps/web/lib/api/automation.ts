import { getApiBaseUrl } from "@/lib/auth/api";
import { ACCESS_TOKEN_COOKIE } from "@/lib/auth/constants";
import type { AutomationWorkflowExport } from "@/lib/studio/automation-flow";

export type AutomationPipelineRecord = {
  id: string;
  tenant_id: string;
  name: string;
  description: string | null;
  is_active: boolean;
  nodes_json: Record<string, unknown>[];
  edges_json: Record<string, unknown>[];
  created_at: string;
  updated_at: string;
};

export type DeployWorkflowInput = {
  workflow: AutomationWorkflowExport;
  pipelineId?: string | null;
  description?: string;
};

function readAccessToken(): string | null {
  if (typeof document === "undefined") return null;
  const prefix = `${ACCESS_TOKEN_COOKIE}=`;
  const match = document.cookie.split(";").map((c) => c.trim()).find((c) => c.startsWith(prefix));
  if (!match) return null;
  return decodeURIComponent(match.slice(prefix.length));
}

async function parseApiError(res: Response): Promise<string> {
  try {
    const body = (await res.json()) as { detail?: string | { msg?: string }[] | { errors?: string[] } };
    if (typeof body.detail === "string") return body.detail;
    if (Array.isArray(body.detail)) return body.detail.map((d) => d.msg).filter(Boolean).join("; ");
    if (body.detail && typeof body.detail === "object" && "errors" in body.detail) {
      const errors = (body.detail as { errors?: string[] }).errors;
      if (errors?.length) return errors.join("; ");
    }
  } catch {
    /* ignore */
  }
  return `Request failed (${res.status})`;
}

function authHeaders(): HeadersInit {
  const token = readAccessToken();
  if (!token) throw new Error("Not signed in — open /login and sign in again.");
  return {
    Accept: "application/json",
    "Content-Type": "application/json",
    Authorization: `Bearer ${token}`,
  };
}

function nodeToJsonRecord(node: AutomationWorkflowExport["nodes"][number]): Record<string, unknown> {
  return { ...node } as Record<string, unknown>;
}

function edgeToJsonRecord(edge: AutomationWorkflowExport["edges"][number]): Record<string, unknown> {
  return { ...edge } as Record<string, unknown>;
}

export function toDeployPayload(workflow: AutomationWorkflowExport) {
  return {
    name: workflow.name || "automation-workflow",
    description: "Deployed from Web HQ Automation Studio",
    is_active: true,
    nodes_json: workflow.nodes.map(nodeToJsonRecord),
    edges_json: workflow.edges.map(edgeToJsonRecord),
  };
}

export async function deployAutomationPipeline(input: DeployWorkflowInput): Promise<AutomationPipelineRecord> {
  const body = toDeployPayload(input.workflow);
  if (input.description) body.description = input.description;

  const base = getApiBaseUrl();
  const headers = authHeaders();

  if (input.pipelineId) {
    const res = await fetch(`${base}/api/v1/automation/pipelines/${input.pipelineId}`, {
      method: "PUT",
      headers,
      body: JSON.stringify(body),
    });
    if (!res.ok) throw new Error(await parseApiError(res));
    return res.json() as Promise<AutomationPipelineRecord>;
  }

  const res = await fetch(`${base}/api/v1/automation/pipelines`, {
    method: "POST",
    headers,
    body: JSON.stringify(body),
  });
  if (!res.ok) throw new Error(await parseApiError(res));
  return res.json() as Promise<AutomationPipelineRecord>;
}
