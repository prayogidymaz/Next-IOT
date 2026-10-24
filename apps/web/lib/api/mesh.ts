import {
  meshEventSchema,
  meshWorkflowDefinitionSchema,
  meshWorkflowRecordSchema,
  workflowDryRunResponseSchema,
  workflowExecutionSchema,
  type MeshEventRecord,
  type MeshWorkflowRecord,
} from "@/lib/api/mesh-schemas";
import { getApiBaseUrl } from "@/lib/auth/api";
import { ACCESS_TOKEN_COOKIE } from "@/lib/auth/constants";
import { z } from "zod";

function readAccessToken(): string | null {
  if (typeof document === "undefined") return null;
  const prefix = `${ACCESS_TOKEN_COOKIE}=`;
  const match = document.cookie.split(";").map((c) => c.trim()).find((c) => c.startsWith(prefix));
  if (!match) return null;
  return decodeURIComponent(match.slice(prefix.length));
}

function authHeaders(): HeadersInit {
  const token = readAccessToken();
  if (!token) throw new Error("Belum masuk — buka /login terlebih dahulu.");
  return {
    Accept: "application/json",
    "Content-Type": "application/json",
    Authorization: `Bearer ${token}`,
  };
}

export async function listMeshEvents(params?: {
  domain?: string;
  event_type?: string;
  device_id?: string;
  limit?: number;
}): Promise<MeshEventRecord[]> {
  const qs = new URLSearchParams();
  if (params?.domain) qs.set("domain", params.domain);
  if (params?.event_type) qs.set("event_type", params.event_type);
  if (params?.device_id) qs.set("device_id", params.device_id);
  if (params?.limit) qs.set("limit", String(params.limit));
  const suffix = qs.size > 0 ? `?${qs.toString()}` : "";
  const res = await fetch(`${getApiBaseUrl()}/api/v1/mesh/events${suffix}`, { headers: authHeaders() });
  if (!res.ok) throw new Error(`Gagal memuat mesh events (${res.status})`);
  const json: unknown = await res.json();
  return z.array(meshEventSchema).parse(json);
}

export async function publishMeshEvent(body: {
  device_id: string;
  domain: string;
  event_type: string;
  payload?: Record<string, unknown>;
  correlation_id?: string;
  parent_event_id?: string;
}): Promise<MeshEventRecord> {
  const res = await fetch(`${getApiBaseUrl()}/api/v1/mesh/events`, {
    method: "POST",
    headers: authHeaders(),
    body: JSON.stringify(body),
  });
  if (!res.ok) throw new Error(`Gagal publish mesh event (${res.status})`);
  const json: unknown = await res.json();
  return meshEventSchema.parse(json);
}

export async function getMeshEventChain(eventId: string): Promise<MeshEventRecord[]> {
  const res = await fetch(`${getApiBaseUrl()}/api/v1/mesh/events/${eventId}/chain`, { headers: authHeaders() });
  if (!res.ok) throw new Error(`Gagal memuat chain (${res.status})`);
  const json: unknown = await res.json();
  return z.array(meshEventSchema).parse(json);
}

export async function listMeshWorkflows(): Promise<MeshWorkflowRecord[]> {
  const res = await fetch(`${getApiBaseUrl()}/api/v1/mesh/workflows`, { headers: authHeaders() });
  if (!res.ok) throw new Error(`Gagal memuat workflows (${res.status})`);
  const json: unknown = await res.json();
  return z.array(meshWorkflowRecordSchema).parse(json);
}

export async function createMeshWorkflow(
  definition: z.infer<typeof meshWorkflowDefinitionSchema>,
): Promise<MeshWorkflowRecord> {
  const res = await fetch(`${getApiBaseUrl()}/api/v1/mesh/workflows`, {
    method: "POST",
    headers: authHeaders(),
    body: JSON.stringify(definition),
  });
  if (!res.ok) throw new Error(`Deploy workflow gagal (${res.status})`);
  const json: unknown = await res.json();
  return meshWorkflowRecordSchema.parse(json);
}

export async function testMeshWorkflow(
  workflowId: string,
  sampleEvent: Record<string, unknown>,
): Promise<z.infer<typeof workflowDryRunResponseSchema>> {
  const res = await fetch(`${getApiBaseUrl()}/api/v1/mesh/workflows/${workflowId}/test`, {
    method: "POST",
    headers: authHeaders(),
    body: JSON.stringify({ sample_event: sampleEvent }),
  });
  if (!res.ok) throw new Error(`Workflow test gagal (${res.status})`);
  const json: unknown = await res.json();
  return workflowDryRunResponseSchema.parse(json);
}

export async function listMeshWorkflowExecutions(workflowId: string): Promise<z.infer<typeof workflowExecutionSchema>[]> {
  const res = await fetch(`${getApiBaseUrl()}/api/v1/mesh/workflows/${workflowId}/executions`, {
    headers: authHeaders(),
  });
  if (!res.ok) throw new Error(`Gagal memuat executions (${res.status})`);
  const json: unknown = await res.json();
  return z.array(workflowExecutionSchema).parse(json);
}

export function meshEventsStreamUrl(): string {
  return `${getApiBaseUrl()}/api/v1/mesh/events/stream`;
}
