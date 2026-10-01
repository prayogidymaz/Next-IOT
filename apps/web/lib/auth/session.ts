import { ACCESS_TOKEN_COOKIE, REFRESH_TOKEN_COOKIE } from "./constants";

const ACCESS_MAX_AGE = 60 * 60; // 1h — align with typical JWT access TTL
const REFRESH_MAX_AGE = 60 * 60 * 24 * 7;

function writeCookie(name: string, value: string, maxAge: number) {
  if (typeof document === "undefined") return;
  const secure = typeof window !== "undefined" && window.location.protocol === "https:" ? "; Secure" : "";
  document.cookie = `${name}=${encodeURIComponent(value)}; Path=/; Max-Age=${maxAge}; SameSite=Lax${secure}`;
}

function deleteCookie(name: string) {
  if (typeof document === "undefined") return;
  document.cookie = `${name}=; Path=/; Max-Age=0; SameSite=Lax`;
}

export function setSessionTokens(accessToken: string, refreshToken: string) {
  writeCookie(ACCESS_TOKEN_COOKIE, accessToken, ACCESS_MAX_AGE);
  writeCookie(REFRESH_TOKEN_COOKIE, refreshToken, REFRESH_MAX_AGE);
}

export function clearSessionTokens() {
  deleteCookie(ACCESS_TOKEN_COOKIE);
  deleteCookie(REFRESH_TOKEN_COOKIE);
}

export function isAccessTokenUsable(token: string | undefined | null): boolean {
  if (!token) return false;
  const parts = token.split(".");
  if (parts.length !== 3) return false;
  try {
    const encoded = parts[1];
    if (!encoded) return false;
    const payload = JSON.parse(atob(encoded.replace(/-/g, "+").replace(/_/g, "/"))) as { exp?: number };
    if (!payload.exp) return true;
    return payload.exp * 1000 > Date.now();
  } catch {
    return false;
  }
}
