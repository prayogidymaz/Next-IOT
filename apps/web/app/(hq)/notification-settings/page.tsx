"use client";

import { useCallback, useEffect, useState } from "react";

import { HqPageContent } from "@/components/hq/HqPageContent";
import { CreamCard } from "@/components/ui/CreamCard";
import { getApiBaseUrl } from "@/lib/auth/api";
import { ACCESS_TOKEN_COOKIE } from "@/lib/auth/constants";

type Channel = { id: string; name: string; channel_type: string; is_active: boolean };

function headers(): HeadersInit {
  const prefix = `${ACCESS_TOKEN_COOKIE}=`;
  const match = document.cookie.split(";").map((c) => c.trim()).find((c) => c.startsWith(prefix));
  const token = match ? decodeURIComponent(match.slice(prefix.length)) : "";
  return { Accept: "application/json", "Content-Type": "application/json", Authorization: `Bearer ${token}` };
}

export default function NotificationSettingsPage() {
  const [channels, setChannels] = useState<Channel[]>([]);
  const reload = useCallback(async () => {
    const res = await fetch(`${getApiBaseUrl()}/api/v1/notification-channels`, { headers: headers() });
    if (res.ok) setChannels((await res.json()) as Channel[]);
  }, []);

  useEffect(() => {
    void reload();
  }, [reload]);

  return (
    <HqPageContent description="Channels, rules, delivery log">
      <CreamCard className="p-4">
        <h2 className="font-semibold">Channels</h2>
        <ul className="mt-2 space-y-1 text-sm">
          {channels.map((c) => (
            <li key={c.id}>
              {c.name} · {c.channel_type} {c.is_active ? "" : "(off)"}
            </li>
          ))}
        </ul>
        <p className="mt-4 text-xs text-ink-secondary">Tambah channel via API POST /notification-channels (UI form MVP).</p>
      </CreamCard>
    </HqPageContent>
  );
}
