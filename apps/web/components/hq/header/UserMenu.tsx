"use client";

import { CircleHelp, LogOut, UserCircle2 } from "lucide-react";
import Link from "next/link";
import { useEffect, useRef, useState } from "react";

import { useHqUser } from "@/hooks/useHqUser";
import { clearSessionTokens } from "@/lib/auth/session";

type Props = {
  showHealthyDot?: boolean;
};

export function UserMenu({ showHealthyDot = false }: Props) {
  const { me, loading } = useHqUser();
  const [open, setOpen] = useState(false);
  const rootRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const onDoc = (e: MouseEvent) => {
      if (rootRef.current && !rootRef.current.contains(e.target as Node)) setOpen(false);
    };
    document.addEventListener("mousedown", onDoc);
    return () => document.removeEventListener("mousedown", onDoc);
  }, []);

  const label = loading ? "…" : (me?.email?.split("@")[0] ?? "User");

  return (
    <div className="relative" ref={rootRef}>
      <button
        type="button"
        onClick={() => setOpen((v) => !v)}
        className="relative inline-flex h-9 items-center gap-2 rounded-lg border border-border bg-card px-2 text-foreground hover:bg-muted"
        aria-label="User menu"
        aria-expanded={open}
      >
        <UserCircle2 className="h-5 w-5 text-accent-cobalt" />
        <span className="hidden max-w-[120px] truncate text-xs font-medium md:inline">{label}</span>
        {showHealthyDot ? (
          <span className="absolute bottom-0.5 right-0.5 h-2 w-2 rounded-full bg-accent-emerald ring-2 ring-card" aria-hidden />
        ) : null}
      </button>
      {open ? (
        <div className="absolute right-0 top-full z-50 mt-1 w-56 rounded-xl border border-border bg-card py-1 shadow-lg">
          <p className="truncate px-3 py-2 text-xs text-muted-foreground">{me?.email ?? "Not signed in"}</p>
          <Link href="/profile" className="block px-3 py-2 text-sm text-foreground hover:bg-muted" onClick={() => setOpen(false)}>
            My profile
          </Link>
          <Link href="/members" className="block px-3 py-2 text-sm text-foreground hover:bg-muted" onClick={() => setOpen(false)}>
            Members & roles
          </Link>
          <Link
            href="/settings/tenant-branding"
            className="block px-3 py-2 text-sm text-foreground hover:bg-muted"
            onClick={() => setOpen(false)}
          >
            Tenant settings
          </Link>
          <Link href="/docs" className="flex items-center gap-2 px-3 py-2 text-sm text-foreground hover:bg-muted" onClick={() => setOpen(false)}>
            <CircleHelp className="h-4 w-4" />
            Help
          </Link>
          <button
            type="button"
            className="flex w-full items-center gap-2 px-3 py-2 text-left text-sm text-foreground hover:bg-muted"
            onClick={() => {
              clearSessionTokens();
              window.location.assign("/login");
            }}
          >
            <LogOut className="h-4 w-4" />
            Log out
          </button>
        </div>
      ) : null}
    </div>
  );
}
