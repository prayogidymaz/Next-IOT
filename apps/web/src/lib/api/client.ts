import { getApiBaseUrl } from "@/lib/auth/api";
import { jsonAuthHeaders, publicJsonHeaders, readApiAccessToken } from "@/lib/auth/api-headers";
import { clearSessionTokens, isAccessTokenUsable } from "@/lib/auth/session";

export const SYSTEM_DEGRADED_EVENT = "next-iot:system-degraded";

export class ApiUnauthorizedError extends Error {
  constructor() {
    super("Session expired");
    this.name = "ApiUnauthorizedError";
  }
}

export function emitSystemDegraded(): void {
  if (typeof window === "undefined") return;
  window.dispatchEvent(new CustomEvent(SYSTEM_DEGRADED_EVENT));
}

export function handleUnauthorized(): void {
  clearSessionTokens();
  if (typeof window === "undefined") return;
  const path = window.location.pathname;
  if (path.startsWith("/login") || path.startsWith("/register")) return;
  window.location.assign("/login");
}

export type ApiFetchInit = RequestInit & {
  /** Skip redirect on 401 (public endpoints). */
  public?: boolean;
  /** Do not attach Authorization header. */
  skipAuth?: boolean;
};

export async function apiFetch(url: string, init: ApiFetchInit = {}): Promise<Response> {
  const headers = new Headers(init.headers);
  if (!init.public && !init.skipAuth) {
    const auth = jsonAuthHeaders(!init.body);
    Object.entries(auth).forEach(([key, value]) => {
      if (!headers.has(key)) headers.set(key, value);
    });
  } else if (!headers.has("Accept")) {
    Object.entries(publicJsonHeaders()).forEach(([key, value]) => headers.set(key, value));
  }

  let res: Response;
  try {
    res = await fetch(url, { ...init, headers });
  } catch {
    emitSystemDegraded();
    throw new Error("Network error");
  }

  if (res.status === 401 && !init.public) {
    handleUnauthorized();
    throw new ApiUnauthorizedError();
  }
  if (res.status >= 500) {
    emitSystemDegraded();
  }
  return res;
}

export function apiUrl(path: string): string {
  const base = getApiBaseUrl().replace(/\/$/, "");
  return path.startsWith("http") ? path : `${base}${path.startsWith("/") ? path : `/${path}`}`;
}

export function isAuthSessionExpired(): boolean {
  const token = readApiAccessToken();
  return !token || !isAccessTokenUsable(token);
}
