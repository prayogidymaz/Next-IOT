import {
  deviceProfileSchema,
  type DeviceProfile,
  type ProfileDomain,
  type ProfileStatus,
  type ThingModelSpec,
} from "@/lib/api/device-profiles-schemas";
import { getApiBaseUrl } from "@/lib/auth/api";
import { ACCESS_TOKEN_COOKIE } from "@/lib/auth/constants";
import { z } from "zod";

export type DeviceProfileCreateInput = {
  key: string;
  name: string;
  description?: string;
  domain: ProfileDomain;
  spec: ThingModelSpec;
};

export type DeviceProfileUpdateInput = {
  name?: string;
  description?: string;
  domain?: ProfileDomain;
  spec?: ThingModelSpec;
};

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

async function readDetail(res: Response): Promise<string> {
  try {
    const body = (await res.json()) as { detail?: string | { msg?: string }[] };
    if (typeof body.detail === "string") return body.detail;
    if (Array.isArray(body.detail)) {
      return body.detail.map((d) => d.msg).filter(Boolean).join("; ");
    }
  } catch {
    /* ignore */
  }
  return `Permintaan gagal (${res.status})`;
}

export function mapDeviceProfileApiError(status: number, detail: string): string {
  const lower = detail.toLowerCase();
  if (status === 409 && lower.includes("only draft")) {
    return "Profil yang sudah published tidak bisa diedit.";
  }
  if (status === 409 && lower.includes("active device")) {
    return "Profil masih dipakai perangkat aktif — tidak bisa diarsipkan.";
  }
  if (status === 409 && lower.includes("published profiles can be assigned")) {
    return "Hanya profil published yang bisa dipasang ke perangkat.";
  }
  if (status === 403) return "Hak akses tidak cukup untuk aksi ini.";
  if (status === 404) return "Profil atau perangkat tidak ditemukan.";
  return detail;
}

async function parseProfileResponse(res: Response): Promise<DeviceProfile> {
  if (!res.ok) {
    const detail = await readDetail(res);
    throw new Error(mapDeviceProfileApiError(res.status, detail));
  }
  const json: unknown = await res.json();
  return deviceProfileSchema.parse(json);
}

export async function listDeviceProfiles(filters?: {
  domain?: ProfileDomain;
  status?: ProfileStatus;
}): Promise<DeviceProfile[]> {
  const params = new URLSearchParams();
  if (filters?.domain) params.set("domain", filters.domain);
  if (filters?.status) params.set("status", filters.status);
  const qs = params.toString();
  const url = `${getApiBaseUrl()}/api/v1/device-profiles${qs ? `?${qs}` : ""}`;
  const res = await fetch(url, { headers: authHeaders() });
  if (!res.ok) {
    const detail = await readDetail(res);
    throw new Error(mapDeviceProfileApiError(res.status, detail));
  }
  const json: unknown = await res.json();
  return z.array(deviceProfileSchema).parse(json);
}

export async function getDeviceProfile(profileId: string): Promise<DeviceProfile> {
  const res = await fetch(`${getApiBaseUrl()}/api/v1/device-profiles/${profileId}`, {
    headers: authHeaders(),
  });
  return parseProfileResponse(res);
}

export async function createDeviceProfile(input: DeviceProfileCreateInput): Promise<DeviceProfile> {
  const res = await fetch(`${getApiBaseUrl()}/api/v1/device-profiles`, {
    method: "POST",
    headers: authHeaders(),
    body: JSON.stringify(input),
  });
  return parseProfileResponse(res);
}

export async function patchDeviceProfile(
  profileId: string,
  input: DeviceProfileUpdateInput,
): Promise<DeviceProfile> {
  const res = await fetch(`${getApiBaseUrl()}/api/v1/device-profiles/${profileId}`, {
    method: "PATCH",
    headers: authHeaders(),
    body: JSON.stringify(input),
  });
  return parseProfileResponse(res);
}

export async function publishDeviceProfile(profileId: string): Promise<DeviceProfile> {
  const res = await fetch(`${getApiBaseUrl()}/api/v1/device-profiles/${profileId}/publish`, {
    method: "POST",
    headers: authHeaders(),
  });
  return parseProfileResponse(res);
}

export async function newVersionDeviceProfile(profileId: string): Promise<DeviceProfile> {
  const res = await fetch(`${getApiBaseUrl()}/api/v1/device-profiles/${profileId}/new-version`, {
    method: "POST",
    headers: authHeaders(),
  });
  return parseProfileResponse(res);
}

export async function archiveDeviceProfile(profileId: string): Promise<DeviceProfile> {
  const res = await fetch(`${getApiBaseUrl()}/api/v1/device-profiles/${profileId}/archive`, {
    method: "POST",
    headers: authHeaders(),
  });
  return parseProfileResponse(res);
}

export async function assignDeviceProfile(deviceId: string, profileId: string | null): Promise<void> {
  const res = await fetch(`${getApiBaseUrl()}/api/v1/devices/${deviceId}/profile`, {
    method: "PATCH",
    headers: authHeaders(),
    body: JSON.stringify({ profile_id: profileId }),
  });
  if (!res.ok) {
    const detail = await readDetail(res);
    throw new Error(mapDeviceProfileApiError(res.status, detail));
  }
}
