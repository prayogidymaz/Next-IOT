import {
  deviceCredentialCreateSchema,
  deviceCredentialPublicSchema,
  type DeviceCredentialCreate,
  type DeviceCredentialPublic,
} from "@/lib/api/mqtt-credentials-schemas";
import { getApiBaseUrl } from "@/lib/auth/api";
import { ACCESS_TOKEN_COOKIE } from "@/lib/auth/constants";

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
    const body = (await res.json()) as { detail?: string };
    if (typeof body.detail === "string") return body.detail;
  } catch {
    /* ignore */
  }
  return `Permintaan gagal (${res.status})`;
}

export async function getDeviceCredential(deviceId: string): Promise<DeviceCredentialPublic | null> {
  const res = await fetch(`${getApiBaseUrl()}/api/v1/devices/${deviceId}/credentials`, {
    headers: authHeaders(),
  });
  if (res.status === 404) return null;
  if (!res.ok) throw new Error(await readDetail(res));
  const json: unknown = await res.json();
  return deviceCredentialPublicSchema.parse(json);
}

export async function generateDeviceCredential(deviceId: string): Promise<DeviceCredentialCreate> {
  const res = await fetch(`${getApiBaseUrl()}/api/v1/devices/${deviceId}/credentials`, {
    method: "POST",
    headers: authHeaders(),
  });
  if (!res.ok) throw new Error(await readDetail(res));
  const json: unknown = await res.json();
  return deviceCredentialCreateSchema.parse(json);
}

export async function rotateDeviceCredential(deviceId: string): Promise<DeviceCredentialCreate> {
  const res = await fetch(`${getApiBaseUrl()}/api/v1/devices/${deviceId}/credentials/rotate`, {
    method: "POST",
    headers: authHeaders(),
  });
  if (!res.ok) throw new Error(await readDetail(res));
  const json: unknown = await res.json();
  return deviceCredentialCreateSchema.parse(json);
}

export async function revokeDeviceCredential(deviceId: string): Promise<void> {
  const res = await fetch(`${getApiBaseUrl()}/api/v1/devices/${deviceId}/credentials`, {
    method: "DELETE",
    headers: authHeaders(),
  });
  if (res.status !== 204) throw new Error(await readDetail(res));
}

export function mqttBrokerUrl(): string {
  return process.env.NEXT_PUBLIC_MQTT_BROKER_URL ?? "mqtt://localhost:11883";
}
