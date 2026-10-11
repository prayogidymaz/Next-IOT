"use client";

import { useRouter } from "next/navigation";
import { useEffect, useState, type ReactNode } from "react";

import { fetchAuthMe } from "@/lib/auth/api";
import { readAccessTokenFromDocument, roleFromAccessToken } from "@/lib/auth/token-role";

export default function SuperAdminLayout({ children }: { children: ReactNode }) {
  const router = useRouter();
  const [allowed, setAllowed] = useState<boolean | null>(null);

  useEffect(() => {
    const token = readAccessTokenFromDocument();
    const quickRole = roleFromAccessToken(token);
    if (quickRole !== "super_admin") {
      router.replace("/devices");
      return;
    }
    if (!token) {
      router.replace("/login");
      return;
    }
    void fetchAuthMe(token)
      .then((me) => {
        if (me.role === "super_admin") setAllowed(true);
        else router.replace("/devices");
      })
      .catch(() => router.replace("/devices"));
  }, [router]);

  if (allowed !== true) {
    return <p className="p-8 text-sm text-ink-secondary">Checking super admin access…</p>;
  }
  return children;
}
