import { z } from "zod";

import { apiFetch, apiUrl } from "@/src/lib/api/client";
import { getApiBaseUrl } from "@/lib/auth/api";
import { jsonAuthHeaders } from "@/lib/auth/api-headers";

const templateSchema = z.object({
  id: z.string().uuid(),
  name: z.string(),
  device_type: z.string(),
  firmware_version: z.string(),
});

export type DeviceConfigTemplate = z.infer<typeof templateSchema>;

const groupSchema = z.object({
  id: z.string().uuid(),
  name: z.string(),
  tag_filter_json: z.record(z.string(), z.unknown()),
});

export type DeviceGroup = z.infer<typeof groupSchema>;

export async function listConfigTemplates(): Promise<DeviceConfigTemplate[]> {
  const res = await apiFetch(apiUrl("/api/v1/fleet/templates"));
  if (!res.ok) throw new Error(`Fleet templates failed (${res.status})`);
  return z.array(templateSchema).parse(await res.json());
}

export async function createConfigTemplate(body: {
  name: string;
  device_type: string;
  config_json: Record<string, unknown>;
  firmware_version: string;
}): Promise<DeviceConfigTemplate> {
  const res = await apiFetch(apiUrl("/api/v1/fleet/templates"), { method: "POST", body: JSON.stringify(body) });
  if (!res.ok) throw new Error(`Create template failed (${res.status})`);
  return templateSchema.parse(await res.json());
}

export async function startBulkProvision(body: { template_id?: string; device_count: number }): Promise<{ job_id: string; status: string }> {
  const res = await apiFetch(apiUrl("/api/v1/fleet/provision"), { method: "POST", body: JSON.stringify(body) });
  if (!res.ok) throw new Error(`Provision failed (${res.status})`);
  return z.object({ job_id: z.string().uuid(), status: z.string() }).parse(await res.json());
}

export function provisionCsvUrl(jobId: string): string {
  return `${getApiBaseUrl()}/api/v1/fleet/provision/${jobId}/csv`;
}

export async function downloadProvisionCsv(jobId: string): Promise<Blob> {
  const res = await fetch(provisionCsvUrl(jobId), { headers: jsonAuthHeaders() });
  if (!res.ok) throw new Error(`CSV download failed (${res.status})`);
  return res.blob();
}

export async function listDeviceGroups(): Promise<DeviceGroup[]> {
  const res = await apiFetch(apiUrl("/api/v1/fleet/groups"));
  if (!res.ok) throw new Error(`Groups failed (${res.status})`);
  return z.array(groupSchema).parse(await res.json());
}

export async function createDeviceGroup(body: { name: string; tag_filter_json: Record<string, unknown> }): Promise<DeviceGroup> {
  const res = await apiFetch(apiUrl("/api/v1/fleet/groups"), { method: "POST", body: JSON.stringify(body) });
  if (!res.ok) throw new Error(`Create group failed (${res.status})`);
  return groupSchema.parse(await res.json());
}

export async function syncGroupConfig(
  groupId: string,
  config: Record<string, unknown>,
): Promise<{ targeted: number; acked: number; ack_rate: number }> {
  const res = await apiFetch(apiUrl(`/api/v1/fleet/groups/${groupId}/sync`), { method: "POST", body: JSON.stringify(config) });
  if (!res.ok) throw new Error(`Sync failed (${res.status})`);
  return z
    .object({ targeted: z.number(), acked: z.number(), ack_rate: z.number() })
    .parse(await res.json());
}
