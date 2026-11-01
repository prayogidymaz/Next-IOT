import * as SecureStore from "expo-secure-store";

const TOKEN_KEY = "next_iot_field_access_token";

export function getApiBaseUrl(): string {
  return process.env.EXPO_PUBLIC_API_URL?.replace(/\/$/, "") ?? "http://10.0.2.2:8000";
}

export async function getStoredToken(): Promise<string | null> {
  return SecureStore.getItemAsync(TOKEN_KEY);
}

export async function setStoredToken(token: string): Promise<void> {
  await SecureStore.setItemAsync(TOKEN_KEY, token);
}

export async function clearStoredToken(): Promise<void> {
  await SecureStore.deleteItemAsync(TOKEN_KEY);
}

type ApiFetchInit = RequestInit & { auth?: boolean };

let unauthorizedHandler: (() => void) | null = null;

export function setUnauthorizedHandler(handler: () => void): void {
  unauthorizedHandler = handler;
}

export async function apiFetch(path: string, init: ApiFetchInit = {}): Promise<Response> {
  const headers = new Headers(init.headers);
  if (!headers.has("Accept")) headers.set("Accept", "application/json");
  if (init.body && !headers.has("Content-Type")) {
    headers.set("Content-Type", "application/json");
  }
  if (init.auth !== false) {
    const token = await getStoredToken();
    if (token) headers.set("Authorization", `Bearer ${token}`);
  }
  const url = path.startsWith("http") ? path : `${getApiBaseUrl()}${path.startsWith("/") ? path : `/${path}`}`;
  if (__DEV__) {
    console.log("[api]", init.method ?? "GET", url);
  }
  const res = await fetch(url, { ...init, headers });
  if (res.status === 401 && init.auth !== false) {
    await clearStoredToken();
    unauthorizedHandler?.();
  }
  if (__DEV__ && !res.ok) {
    console.warn("[api] response", res.status, url);
  }
  return res;
}
