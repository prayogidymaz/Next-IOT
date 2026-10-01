const DEFAULT_DEV_API = "http://localhost:8000";

export function getApiBaseUrl(): string {
  const fromEnv = process.env.NEXT_PUBLIC_API_URL?.replace(/\/$/, "");
  if (fromEnv) return fromEnv;

  if (typeof window !== "undefined") {
    const { hostname, port, origin } = window.location;
    // Next.js dev server — API runs on FastAPI :8000, not :3000
    if (hostname === "localhost" || hostname === "127.0.0.1") {
      if (port === "3000" || port === "") {
        return DEFAULT_DEV_API;
      }
    }
    return origin;
  }

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
  });
  if (!res.ok) throw new Error(await parseError(res));
  return res.json() as Promise<TokenResponse>;
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
  const data = (await res.json()) as { tokens: TokenResponse };
  return data;
}

export async function fetchAuthMe(accessToken: string): Promise<AuthUser> {
  const res = await fetch(`${getApiBaseUrl()}/api/v1/auth/me`, {
    headers: {
      Accept: "application/json",
      Authorization: `Bearer ${accessToken}`,
    },
  });
  if (!res.ok) throw new Error(await parseError(res));
  return res.json() as Promise<AuthUser>;
}
