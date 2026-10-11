"use client";

import { useRouter } from "next/navigation";
import { useEffect, useState, type ReactNode } from "react";

import { fetchAuthMe } from "@/lib/auth/api";
import { readAccessTokenFromDocument, roleFromAccessToken } from "@/lib/auth/token-role";

export default function AdminProtectedLayout({ children }: { children: ReactNode }) {
  const router = useRouter();
  const [allowed, setAllowed] = useState<boolean | null>(null);

  useEffect(() => {
    const token = readAccessTokenFromDocument();
    if (!token || roleFromAccessToken(token) !== "super_admin") {
      router.replace("/login");
      return;
    }
    void fetchAuthMe(token)
      .then((me) => {
        if (me.role === "super_admin") setAllowed(true);
        else router.replace("/login?error=super_admin_required");
      })
      .catch(() => router.replace("/login"));
  }, [router]);

  if (allowed !== true) {
    return <p className="p-8 font-mono text-sm text-command-secondary">Verifying operator clearance…</p>;
  }
  return children;
}
