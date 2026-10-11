"use client";

import {
  createContext,
  useCallback,
  useContext,
  useEffect,
  useMemo,
  useState,
  type ReactNode,
} from "react";

import { fetchAuthMe } from "@/lib/auth/api";
import { readAccessTokenFromDocument } from "@/lib/auth/token-role";
import type { HqDomainId } from "@/lib/hq/domains";

const TENANTS: string[] = ["Next-IoT Platform", "Acme Agri Co", "SkyLogistics Fleet"];
const DEFAULT_TENANT = TENANTS[0] ?? "Next-IoT Platform";

type HqShellContextValue = {
  collapsed: boolean;
  toggleCollapsed: () => void;
  tenant: string;
  setTenant: (t: string) => void;
  tenants: string[];
  domainId: HqDomainId;
  setDomainId: (id: HqDomainId) => void;
  notificationCount: number;
  systemHealth: "healthy" | "degraded" | "unknown";
  userRole: string | null;
};

const HqShellContext = createContext<HqShellContextValue | null>(null);

export function HqShellProvider({ children }: { children: ReactNode }) {
  const [collapsed, setCollapsed] = useState(false);
  const [tenant, setTenant] = useState<string>(DEFAULT_TENANT);
  const [domainId, setDomainId] = useState<HqDomainId>("smart-home");
  const [systemHealth, setSystemHealth] = useState<HqShellContextValue["systemHealth"]>("unknown");
  const [userRole, setUserRole] = useState<string | null>(null);

  useEffect(() => {
    const stored = localStorage.getItem("hq_sidebar_collapsed");
    if (stored === "1") setCollapsed(true);
    const storedDomain = localStorage.getItem("hq_domain_id") as HqDomainId | null;
    if (storedDomain) setDomainId(storedDomain);
    const storedTenant = localStorage.getItem("hq_tenant");
    if (storedTenant && TENANTS.includes(storedTenant)) setTenant(storedTenant);
  }, []);

  useEffect(() => {
    localStorage.setItem("hq_sidebar_collapsed", collapsed ? "1" : "0");
  }, [collapsed]);

  useEffect(() => {
    localStorage.setItem("hq_domain_id", domainId);
  }, [domainId]);

  useEffect(() => {
    localStorage.setItem("hq_tenant", tenant);
  }, [tenant]);

  useEffect(() => {
    const token = readAccessTokenFromDocument();
    if (token) {
      void fetchAuthMe(token)
        .then((me) => setUserRole(me.role))
        .catch(() => setUserRole(null));
    }
  }, []);

  useEffect(() => {
    let cancelled = false;
    (async () => {
      try {
        const base =
          process.env.NEXT_PUBLIC_API_URL?.replace(/\/$/, "") ?? "http://localhost:8000";
        const res = await fetch(`${base}/health`, { cache: "no-store" });
        if (!res.ok) throw new Error("bad status");
        const data = (await res.json()) as { status?: string };
        if (!cancelled) setSystemHealth(data.status === "healthy" ? "healthy" : "degraded");
      } catch {
        if (!cancelled) setSystemHealth("degraded");
      }
    })();
    return () => {
      cancelled = true;
    };
  }, []);

  const toggleCollapsed = useCallback(() => setCollapsed((c) => !c), []);

  const value = useMemo(
    () => ({
      collapsed,
      toggleCollapsed,
      tenant,
      setTenant,
      tenants: TENANTS,
      domainId,
      setDomainId,
      notificationCount: 3,
      systemHealth,
      userRole,
    }),
    [collapsed, toggleCollapsed, tenant, domainId, systemHealth, userRole],
  );

  return <HqShellContext.Provider value={value}>{children}</HqShellContext.Provider>;
}

export function useHqShell() {
  const ctx = useContext(HqShellContext);
  if (!ctx) throw new Error("useHqShell must be used within HqShellProvider");
  return ctx;
}
