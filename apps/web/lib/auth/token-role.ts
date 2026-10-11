import { ACCESS_TOKEN_COOKIE } from "@/lib/auth/constants";

type JwtPayload = {
  role?: string;
  exp?: number;
};

export function readAccessTokenFromDocument(): string | null {
  if (typeof document === "undefined") return null;
  const prefix = `${ACCESS_TOKEN_COOKIE}=`;
  const match = document.cookie.split(";").map((c) => c.trim()).find((c) => c.startsWith(prefix));
  return match ? decodeURIComponent(match.slice(prefix.length)) : null;
}

export function roleFromAccessToken(token: string | undefined | null): string | null {
  if (!token) return null;
  const parts = token.split(".");
  if (parts.length !== 3) return null;
  try {
    const encoded = parts[1];
    if (!encoded) return null;
    const payload = JSON.parse(atob(encoded.replace(/-/g, "+").replace(/_/g, "/"))) as JwtPayload;
    return typeof payload.role === "string" ? payload.role : null;
  } catch {
    return null;
  }
}

export function readRoleFromDocumentCookie(): string | null {
  return roleFromAccessToken(readAccessTokenFromDocument());
}
