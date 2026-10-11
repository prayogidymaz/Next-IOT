import { getApiBaseUrl } from "@/lib/auth/api";
import { ACCESS_TOKEN_COOKIE } from "@/lib/auth/constants";

function authHeaders(): HeadersInit {
  const prefix = `${ACCESS_TOKEN_COOKIE}=`;
  const match = document.cookie.split(";").map((c) => c.trim()).find((c) => c.startsWith(prefix));
  const token = match ? decodeURIComponent(match.slice(prefix.length)) : null;
  if (!token) throw new Error("Belum masuk");
  return { Accept: "application/json", "Content-Type": "application/json", Authorization: `Bearer ${token}` };
}

export async function previewFirmware(body: unknown): Promise<{ main_cpp: string }> {
  const res = await fetch(`${getApiBaseUrl()}/api/v1/firmware-studio/preview`, {
    method: "POST",
    headers: authHeaders(),
    body: JSON.stringify(body),
  });
  if (!res.ok) throw new Error(await res.text());
  return (await res.json()) as { main_cpp: string };
}

export async function downloadFirmwareZip(body: unknown): Promise<Blob> {
  const res = await fetch(`${getApiBaseUrl()}/api/v1/firmware-studio/generate`, {
    method: "POST",
    headers: authHeaders(),
    body: JSON.stringify(body),
  });
  if (!res.ok) throw new Error(await res.text());
  return res.blob();
}

export async function listDeviceProfiles(): Promise<Array<{ id: string; name: string; key: string }>> {
  const res = await fetch(`${getApiBaseUrl()}/api/v1/device-profiles`, { headers: authHeaders() });
  if (!res.ok) throw new Error(`Profiles (${res.status})`);
  return (await res.json()) as Array<{ id: string; name: string; key: string }>;
}
