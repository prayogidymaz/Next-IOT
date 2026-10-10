import {
  deviceAttributeItemSchema,
  deviceAttributeListSchema,
  type DeviceAttributeItem,
} from "@/lib/api/device-attributes-schemas";
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

export async function listDeviceAttributes(
  deviceId: string,
  scope?: "server" | "shared" | "client",
): Promise<DeviceAttributeItem[]> {
  const qs = scope ? `?scope=${scope}` : "";
  const res = await fetch(`${getApiBaseUrl()}/api/v1/devices/${deviceId}/attributes${qs}`, {
    headers: authHeaders(),
  });
  if (!res.ok) throw new Error(`Gagal memuat attributes (${res.status})`);
  return deviceAttributeListSchema.parse(await res.json()).items;
}

export async function putDeviceAttribute(
  deviceId: string,
  scope: "server" | "shared",
  key: string,
  value: unknown,
): Promise<DeviceAttributeItem> {
  const res = await fetch(
    `${getApiBaseUrl()}/api/v1/devices/${deviceId}/attributes/${scope}/${key}`,
    {
      method: "PUT",
      headers: authHeaders(),
      body: JSON.stringify({ value }),
    },
  );
  if (!res.ok) throw new Error(`Gagal menyimpan attribute (${res.status})`);
  const body = (await res.json()) as {
    key: string;
    scope: string;
    value: unknown;
    updated_at: string;
  };
  return deviceAttributeItemSchema.parse({
    key: body.key,
    scope: body.scope,
    value: body.value,
    updated_at: body.updated_at,
    updated_by_user_id: null,
    updated_source: "api",
  });
}

export async function deleteDeviceAttribute(
  deviceId: string,
  scope: "server" | "shared" | "client",
  key: string,
): Promise<void> {
  const res = await fetch(
    `${getApiBaseUrl()}/api/v1/devices/${deviceId}/attributes/${scope}/${key}`,
    { method: "DELETE", headers: authHeaders() },
  );
  if (!res.ok && res.status !== 204) throw new Error(`Gagal menghapus attribute (${res.status})`);
}
