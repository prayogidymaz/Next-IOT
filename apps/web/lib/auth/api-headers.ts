import { readAccessTokenFromDocument } from "@/lib/auth/token-role";

/** HQ session token (cookie first, then legacy localStorage). */
export function readApiAccessToken(): string | null {
  if (typeof window === "undefined") return null;
  const fromCookie = readAccessTokenFromDocument();
  if (fromCookie) return fromCookie;
  const legacy = localStorage.getItem("access_token");
  return legacy && legacy.length > 0 ? legacy : null;
}

export function jsonAuthHeaders(includeBodyContentType = true): HeadersInit {
  const headers: Record<string, string> = { Accept: "application/json" };
  if (includeBodyContentType) headers["Content-Type"] = "application/json";
  const token = readApiAccessToken();
  if (token) headers.Authorization = `Bearer ${token}`;
  return headers;
}

export function publicJsonHeaders(): HeadersInit {
  return { Accept: "application/json" };
}

export async function apiErrorMessage(res: Response): Promise<string> {
  const text = await res.text();
  return text.length > 0 ? text : `Request failed (${res.status})`;
}
