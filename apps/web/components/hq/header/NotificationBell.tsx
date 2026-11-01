"use client";

import { Bell } from "lucide-react";
import Link from "next/link";
import { useCallback, useEffect, useRef, useState } from "react";

import { acknowledgeAlarm, listAlarms, type AlarmItem } from "@/lib/api/alarms";
import { useHqShell } from "@/lib/hq/hq-shell-context";

export function NotificationBell() {
  const { alarmCount } = useHqShell();
  const [open, setOpen] = useState(false);
  const [items, setItems] = useState<AlarmItem[]>([]);
  const [loading, setLoading] = useState(false);
  const rootRef = useRef<HTMLDivElement>(null);

  const reload = useCallback(async () => {
    setLoading(true);
    try {
      setItems(await listAlarms({ status: "active" }));
    } catch {
      setItems([]);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    if (!open) return;
    void reload();
  }, [open, reload]);

  useEffect(() => {
    const onDoc = (e: MouseEvent) => {
      if (rootRef.current && !rootRef.current.contains(e.target as Node)) setOpen(false);
    };
    document.addEventListener("mousedown", onDoc);
    return () => document.removeEventListener("mousedown", onDoc);
  }, []);

  async function markAllRead() {
    const active = items.filter((a) => a.status === "active");
    await Promise.all(active.map((a) => acknowledgeAlarm(a.id).catch(() => undefined)));
    await reload();
  }

  return (
    <div className="relative" ref={rootRef}>
      <button
        type="button"
        onClick={() => setOpen((v) => !v)}
        className="relative inline-flex h-9 w-9 items-center justify-center rounded-lg border border-border bg-card text-foreground hover:bg-muted"
        aria-label="Notifications"
        aria-expanded={open}
      >
        <Bell className="h-4 w-4" />
        {alarmCount > 0 ? (
          <span className="absolute -right-1 -top-1 flex h-4 min-w-4 items-center justify-center rounded-full bg-accent-amber px-1 text-[10px] font-bold text-white">
            {alarmCount > 99 ? "99+" : alarmCount}
          </span>
        ) : null}
      </button>
      {open ? (
        <div className="absolute right-0 top-full z-50 mt-1 w-80 rounded-xl border border-border bg-card shadow-lg">
          <div className="flex items-center justify-between border-b border-border px-3 py-2">
            <span className="text-sm font-medium text-foreground">Notifications</span>
            <button
              type="button"
              className="text-xs text-muted-foreground hover:text-foreground disabled:opacity-50"
              disabled={loading || items.length === 0}
              onClick={() => void markAllRead()}
            >
              Mark all read
            </button>
          </div>
          <ul className="max-h-72 overflow-y-auto p-2">
            {loading ? (
              <li className="px-2 py-3 text-sm text-muted-foreground">Loading…</li>
            ) : items.length === 0 ? (
              <li className="px-2 py-3 text-sm text-muted-foreground">No active alarms</li>
            ) : (
              items.slice(0, 8).map((a) => (
                <li key={a.id}>
                  <Link
                    href="/alarms"
                    className="block rounded-lg px-2 py-2 text-sm hover:bg-muted"
                    onClick={() => setOpen(false)}
                  >
                    <span className="font-medium text-foreground">{a.title}</span>
                    <span className="mt-0.5 block text-xs text-muted-foreground">{a.severity} · {a.status}</span>
                  </Link>
                </li>
              ))
            )}
          </ul>
          <div className="border-t border-border px-3 py-2">
            <Link href="/alarms" className="text-xs font-medium text-accent-cobalt hover:underline" onClick={() => setOpen(false)}>
              View all alarms
            </Link>
            <span className="mx-2 text-muted-foreground">·</span>
            <Link
              href="/notification-settings"
              className="text-xs font-medium text-muted-foreground hover:text-foreground"
              onClick={() => setOpen(false)}
            >
              Channel settings
            </Link>
          </div>
        </div>
      ) : null}
    </div>
  );
}
