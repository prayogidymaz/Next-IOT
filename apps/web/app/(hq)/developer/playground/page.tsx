"use client";

import { useMemo, useState } from "react";

import { FadeInPage } from "@/components/motion/FadeInPage";
import { getApiBaseUrl } from "@/lib/auth/api";
import { readApiAccessToken } from "@/lib/auth/api-headers";
import { Button } from "@/components/ui/button";

const ENDPOINTS = [
  { method: "GET", path: "/api/v1/sites" },
  { method: "GET", path: "/api/v1/sustainability/carbon" },
  { method: "GET", path: "/api/v1/webhooks" },
  { method: "GET", path: "/api/v1/marketplace/templates" },
] as const;

export default function ApiPlaygroundPage() {
  const [idx, setIdx] = useState(0);
  const [response, setResponse] = useState("");
  const [loading, setLoading] = useState(false);

  const ep = ENDPOINTS[idx] ?? ENDPOINTS[0];
  const curlSnippet = useMemo(() => {
    const token = readApiAccessToken() ?? "TOKEN";
    return `curl -s -H "Authorization: Bearer ${token}" "${getApiBaseUrl()}${ep.path}"`;
  }, [ep.path]);

  async function tryIt() {
    setLoading(true);
    try {
      const res = await fetch(`${getApiBaseUrl()}${ep.path}`, {
        headers: { Authorization: `Bearer ${readApiAccessToken() ?? ""}`, Accept: "application/json" },
      });
      const text = await res.text();
      setResponse(`${res.status}\n${text}`);
    } catch (e: unknown) {
      setResponse(e instanceof Error ? e.message : "Request failed");
    } finally {
      setLoading(false);
    }
  }

  return (
    <FadeInPage>
      <div className="container mx-auto max-w-3xl space-y-4 px-4 py-4 md:px-6 lg:px-8">
        <div className="flex flex-wrap gap-2">
          <select
            className="rounded-lg border border-border bg-card px-3 py-2 text-sm text-foreground"
            value={idx}
            onChange={(e) => setIdx(Number(e.target.value))}
          >
            {ENDPOINTS.map((e, i) => (
              <option key={e.path} value={i}>
                {e.method} {e.path}
              </option>
            ))}
          </select>
          <Button type="button" onClick={() => void tryIt()} disabled={loading}>
            {loading ? "Sending…" : "Try it"}
          </Button>
        </div>
        <pre className="overflow-x-auto rounded-xl border border-border bg-muted/30 p-3 text-xs text-foreground">{curlSnippet}</pre>
        <pre className="min-h-[12rem] overflow-x-auto rounded-xl border border-border bg-card p-3 text-xs text-muted-foreground whitespace-pre-wrap">
          {response || "Response will appear here."}
        </pre>
      </div>
    </FadeInPage>
  );
}
