import { z } from "zod";

import { getApiBaseUrl } from "@/lib/auth/api";
import { ACCESS_TOKEN_COOKIE } from "@/lib/auth/constants";

import {
  firmwareReleaseSchema,
  otaPublishResponseSchema,
  otaRolloutSchema,
  type FirmwareRelease,
  type OtaRollout,
} from "./firmware-releases-schemas";

function bearerToken(): string {
  const prefix = `${ACCESS_TOKEN_COOKIE}=`;
  const match = document.cookie.split(";").map((c) => c.trim()).find((c) => c.startsWith(prefix));
  const token = match ? decodeURIComponent(match.slice(prefix.length)) : null;
  if (!token) throw new Error("Belum masuk");
  return token;
}

export async function listFirmwareReleases(): Promise<FirmwareRelease[]> {
  const res = await fetch(`${getApiBaseUrl()}/api/v1/ota/releases`, {
    headers: { Accept: "application/json", Authorization: `Bearer ${bearerToken()}` },
  });
  if (!res.ok) throw new Error(`Releases (${res.status})`);
  const json: unknown = await res.json();
  return z.array(firmwareReleaseSchema).parse(json);
}

export async function uploadFirmwareRelease(params: {
  file: File;
  version: string;
  targetDeviceCategory: string;
}): Promise<FirmwareRelease> {
  const form = new FormData();
  form.append("file", params.file);
  form.append("version", params.version);
  form.append("target_device_category", params.targetDeviceCategory);
  const res = await fetch(`${getApiBaseUrl()}/api/v1/ota/releases`, {
    method: "POST",
    headers: { Authorization: `Bearer ${bearerToken()}` },
    body: form,
  });
  if (!res.ok) throw new Error(await res.text());
  return firmwareReleaseSchema.parse(await res.json());
}

export async function publishFirmwareRelease(releaseId: string): Promise<{
  targeted_devices: number;
  rollouts_created: number;
}> {
  const res = await fetch(`${getApiBaseUrl()}/api/v1/ota/releases/${releaseId}/publish`, {
    method: "POST",
    headers: { Accept: "application/json", Authorization: `Bearer ${bearerToken()}` },
  });
  if (!res.ok) throw new Error(await res.text());
  const parsed = otaPublishResponseSchema.parse(await res.json());
  return {
    targeted_devices: parsed.targeted_devices,
    rollouts_created: parsed.rollouts_created,
  };
}

export async function listReleaseRollouts(releaseId: string): Promise<OtaRollout[]> {
  const res = await fetch(`${getApiBaseUrl()}/api/v1/ota/releases/${releaseId}/rollouts`, {
    headers: { Accept: "application/json", Authorization: `Bearer ${bearerToken()}` },
  });
  if (!res.ok) throw new Error(`Rollouts (${res.status})`);
  const json: unknown = await res.json();
  return z.array(otaRolloutSchema).parse(json);
}

export type { FirmwareRelease, OtaRollout } from "./firmware-releases-schemas";
