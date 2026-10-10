import {
  deviceRpcCreateResponseSchema,
  deviceRpcListSchema,
  type DeviceRpcItem,
} from "@/lib/api/device-rpc-schemas";
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

export async function listDeviceRpc(deviceId: string): Promise<DeviceRpcItem[]> {
  const res = await fetch(`${getApiBaseUrl()}/api/v1/devices/${deviceId}/rpc`, {
    headers: authHeaders(),
  });
  if (!res.ok) throw new Error(`Gagal memuat RPC history (${res.status})`);
  return deviceRpcListSchema.parse(await res.json()).items;
}

export async function sendDeviceRpc(
  deviceId: string,
  body: { method: string; params: Record<string, unknown>; timeout_seconds?: number },
): Promise<{ status: number; body: ReturnType<typeof deviceRpcCreateResponseSchema.parse> }> {
  const res = await fetch(`${getApiBaseUrl()}/api/v1/devices/${deviceId}/rpc`, {
    method: "POST",
    headers: authHeaders(),
    body: JSON.stringify({
      method: body.method,
      params: body.params,
      timeout_seconds: body.timeout_seconds ?? 30,
    }),
  });
  const json: unknown = await res.json();
  return { status: res.status, body: deviceRpcCreateResponseSchema.parse(json) };
}
