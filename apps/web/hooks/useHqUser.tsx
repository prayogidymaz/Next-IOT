"use client";

import {
  createContext,
  useContext,
  useEffect,
  useMemo,
  useState,
  type ReactNode,
} from "react";
import { z } from "zod";

import { getApiBaseUrl } from "@/lib/auth/api";
import { ACCESS_TOKEN_COOKIE } from "@/lib/auth/constants";
import { canWriteDeviceProfiles } from "@/lib/hq/rbac";

const meSchema = z.object({
  user_id: z.string(),
  email: z.string(),
  role: z.string(),
  tenant_id: z.string(),
  security_tier: z.string(),
  tier_level: z.number(),
});

export type HqMe = z.infer<typeof meSchema>;

type HqUserContextValue = {
  me: HqMe | null;
  loading: boolean;
  canWriteProfiles: boolean;
};

const HqUserContext = createContext<HqUserContextValue | null>(null);

function readAccessToken(): string | null {
  if (typeof document === "undefined") return null;
  const prefix = `${ACCESS_TOKEN_COOKIE}=`;
  const match = document.cookie.split(";").map((c) => c.trim()).find((c) => c.startsWith(prefix));
  if (!match) return null;
  return decodeURIComponent(match.slice(prefix.length));
}

export function HqUserProvider({ children }: { children: ReactNode }) {
  const [me, setMe] = useState<HqMe | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    let cancelled = false;
    (async () => {
      const token = readAccessToken();
      if (!token) {
        if (!cancelled) setLoading(false);
        return;
      }
      try {
        const res = await fetch(`${getApiBaseUrl()}/api/v1/me`, {
          headers: { Accept: "application/json", Authorization: `Bearer ${token}` },
        });
        if (!res.ok) throw new Error("me failed");
        const json: unknown = await res.json();
        const parsed = meSchema.parse(json);
        if (!cancelled) setMe(parsed);
      } catch {
        if (!cancelled) setMe(null);
      } finally {
        if (!cancelled) setLoading(false);
      }
    })();
    return () => {
      cancelled = true;
    };
  }, []);

  const value = useMemo(
    () => ({
      me,
      loading,
      canWriteProfiles: canWriteDeviceProfiles(me?.role),
    }),
    [me, loading],
  );

  return <HqUserContext.Provider value={value}>{children}</HqUserContext.Provider>;
}

export function useHqUser() {
  const ctx = useContext(HqUserContext);
  if (!ctx) throw new Error("useHqUser must be used within HqUserProvider");
  return ctx;
}
