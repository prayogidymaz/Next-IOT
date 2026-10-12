import { authUserSchema, registerResponseSchema, tokenResponseSchema } from "@/lib/auth/schemas";

const DEFAULT_DEV_API = "http://localhost:8000";

export function getApiBaseUrl(): string {
  if (typeof window !== "undefined") {
    const { hostname, port, origin } = window.location;
    // Use same-origin /api rewrite (see next.config) so admin :3001 does not call itself or hang on :8000 reload.
    if (hostname === "localhost" || hostname === "127.0.0.1") {
      if (port === "3000" || port === "3001" || port === "3002" || port === "") {
        return origin;
      }
    }
  }

  const fromEnv = process.env.NEXT_PUBLIC_API_URL?.replace(/\/$/, "");
  if (fromEnv) return fromEnv;

  return DEFAULT_DEV_API;
}

export type AuthUser = {
  user_id: string;
  email: string;
  role: string;
  tenant_id: string;
  permissions: string[];
};

export type TokenResponse = {
  access_token: string;
  refresh_token: string;
  token_type: string;
  role?: string;
  email?: string;
};

async function parseError(res: Response): Promise<string> {
  try {
    const body = (await res.json()) as { detail?: string | { msg?: string }[] };
    if (typeof body.detail === "string") return body.detail;
    if (Array.isArray(body.detail) && body.detail[0]?.msg) return body.detail[0].msg;
  } catch {
    /* ignore */
  }
  return `Request failed (${res.status})`;
}

export async function login(email: string, password: string): Promise<TokenResponse> {
  const res = await fetch(`${getApiBaseUrl()}/api/v1/auth/login`, {
    method: "POST",
    headers: { "Content-Type": "application/json", Accept: "application/json" },
    body: JSON.stringify({ email, password }),
    signal: AbortSignal.timeout(30_000),
  });
  if (!res.ok) throw new Error(await parseError(res));
  const json: unknown = await res.json();
  return tokenResponseSchema.parse(json);
}

export async function register(input: {
  email: string;
  password: string;
  tenant_name?: string;
  tenant_slug?: string;
}): Promise<{ tokens: TokenResponse }> {
  const res = await fetch(`${getApiBaseUrl()}/api/v1/auth/register`, {
    method: "POST",
    headers: { "Content-Type": "application/json", Accept: "application/json" },
    body: JSON.stringify(input),
  });
  if (!res.ok) throw new Error(await parseError(res));
  const json: unknown = await res.json();
  return registerResponseSchema.parse(json);
}

export async function fetchAuthMe(accessToken: string): Promise<AuthUser> {
  const res = await fetch(`${getApiBaseUrl()}/api/v1/auth/me`, {
    headers: {
      Accept: "application/json",
      Authorization: `Bearer ${accessToken}`,
    },
  });
  if (!res.ok) throw new Error(await parseError(res));
  const json: unknown = await res.json();
  return authUserSchema.parse(json);
}
