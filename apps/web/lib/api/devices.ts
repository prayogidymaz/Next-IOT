import { deviceResponseSchema, type DeviceResponse } from "@/lib/api/devices-schemas";
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
    Authorization: `Bearer ${token}`,
  };
}

export async function listDevices(): Promise<DeviceResponse[]> {
  const res = await fetch(`${getApiBaseUrl()}/api/v1/devices`, { headers: authHeaders() });
  if (!res.ok) throw new Error(`Gagal memuat perangkat (${res.status})`);
  const json: unknown = await res.json();
  return z.array(deviceResponseSchema).parse(json);
}

export async function getDevice(deviceId: string): Promise<DeviceResponse> {
  const res = await fetch(`${getApiBaseUrl()}/api/v1/devices/${deviceId}`, { headers: authHeaders() });
  if (!res.ok) throw new Error(`Perangkat tidak ditemukan (${res.status})`);
  const json: unknown = await res.json();
  return deviceResponseSchema.parse(json);
}
