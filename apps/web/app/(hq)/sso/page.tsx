"use client";

import { useCallback, useEffect, useState } from "react";

import { HqPageShell } from "@/components/hq/HqPageShell";
import { apiFetch, apiUrl } from "@/src/lib/api/client";
import { Button } from "@/components/ui/button";

type SsoRow = { provider: string; client_id: string; enabled: boolean };

export default function SsoPage() {
  const [rows, setRows] = useState<SsoRow[]>([]);
  const [provider, setProvider] = useState("google");
  const [clientId, setClientId] = useState("");
  const [clientSecret, setClientSecret] = useState("");

  const load = useCallback(async () => {
    const res = await apiFetch(apiUrl("/api/v1/auth/sso"));
    if (res.ok) setRows((await res.json()) as SsoRow[]);
  }, []);

  useEffect(() => {
    void load();
  }, [load]);

  async function save(enabled: boolean) {
    await apiFetch(apiUrl(`/api/v1/auth/sso/${provider}`), {
      method: "PUT",
      body: JSON.stringify({ provider, client_id: clientId, client_secret: clientSecret, enabled }),
    });
    await load();
  }

  return (
    <HqPageShell>
      <div className="mx-auto max-w-xl space-y-4">
        <p className="text-sm text-muted-foreground">Configure OAuth2 (Google / Microsoft). SAML integration TODO.</p>
        <select className="w-full rounded-lg border border-border bg-card px-3 py-2 text-sm" value={provider} onChange={(e) => setProvider(e.target.value)}>
          <option value="google">Google</option>
          <option value="microsoft">Microsoft</option>
        </select>
        <input className="w-full rounded-lg border border-border bg-card px-3 py-2 text-sm" placeholder="Client ID" value={clientId} onChange={(e) => setClientId(e.target.value)} />
        <input className="w-full rounded-lg border border-border bg-card px-3 py-2 text-sm" placeholder="Client secret" type="password" value={clientSecret} onChange={(e) => setClientSecret(e.target.value)} />
        <div className="flex gap-2">
          <Button type="button" onClick={() => void save(true)}>
            Save & enable
          </Button>
          <Button type="button" variant="outline" onClick={() => void save(false)}>
            Disable
          </Button>
        </div>
        <ul className="text-sm text-muted-foreground">
          {rows.map((r) => (
            <li key={r.provider}>
              {r.provider}: {r.enabled ? "enabled" : "disabled"} ({r.client_id})
            </li>
          ))}
        </ul>
      </div>
    </HqPageShell>
  );
}
