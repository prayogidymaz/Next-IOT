import {
  claimTokenCreateSchema,
  claimTokenSchema,
  type ClaimToken,
  type ClaimTokenCreateInput,
} from "@/lib/api/claim-tokens-schemas";
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

async function readDetail(res: Response): Promise<string> {
  try {
    const body = (await res.json()) as { detail?: string };
    if (typeof body.detail === "string") return body.detail;
  } catch {
    /* ignore */
  }
  return `Permintaan gagal (${res.status})`;
}

export async function listClaimTokens(): Promise<ClaimToken[]> {
  const res = await fetch(`${getApiBaseUrl()}/api/v1/device-claim-tokens`, { headers: authHeaders() });
  if (!res.ok) throw new Error(await readDetail(res));
  const json: unknown = await res.json();
  return z.array(claimTokenSchema).parse(json);
}

export async function createClaimToken(input: ClaimTokenCreateInput): Promise<ClaimToken> {
  const res = await fetch(`${getApiBaseUrl()}/api/v1/device-claim-tokens`, {
    method: "POST",
    headers: authHeaders(),
    body: JSON.stringify(claimTokenCreateSchema.parse(input)),
  });
  if (!res.ok) throw new Error(await readDetail(res));
  const json: unknown = await res.json();
  return claimTokenSchema.parse(json);
}

export async function revokeClaimToken(tokenId: string): Promise<void> {
  const res = await fetch(`${getApiBaseUrl()}/api/v1/device-claim-tokens/${tokenId}`, {
    method: "DELETE",
    headers: authHeaders(),
  });
  if (res.status !== 204) throw new Error(await readDetail(res));
}

export function claimQrPayload(qrCodeUrl: string, claimToken: string): string {
  if (qrCodeUrl.startsWith("nextiot://")) return qrCodeUrl;
  return `nextiot://claim?token=${claimToken}`;
}
