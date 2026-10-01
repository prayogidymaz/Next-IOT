"use client";

import { Gauge, Key, Webhook } from "lucide-react";

import { HqPageContent } from "@/components/hq/HqPageContent";
import { CreamCard } from "@/components/ui/CreamCard";

const KEYS = [
  { name: "Production ingest", prefix: "ni_live_••••8f2a", scope: "telemetry.write", status: "Active" },
  { name: "Partner webhook", prefix: "ni_wh_••••91bd", scope: "webhooks.manage", status: "Active" },
  { name: "Staging QA", prefix: "ni_test_••••c011", scope: "devices.read", status: "Rotating" },
];

export default function DeveloperApiKeysPage() {
  return (
    <HqPageContent description="Manage PAT keys, webhook endpoints, and rate-limit monitors for the Open API segment.">
      <div className="grid gap-4 md:grid-cols-3">
        <CreamCard hover className="p-5">
          <div className="flex items-center gap-3">
            <span className="rounded-xl bg-accent-indigo-soft p-2.5">
              <Key className="h-5 w-5 text-accent-indigo" />
            </span>
            <div>
              <p className="text-sm text-ink-secondary">Active keys</p>
              <p className="text-2xl font-semibold text-ink-primary">3</p>
            </div>
          </div>
        </CreamCard>
        <CreamCard hover className="p-5">
          <div className="flex items-center gap-3">
            <span className="rounded-xl bg-accent-emerald-soft p-2.5">
              <Webhook className="h-5 w-5 text-accent-emerald" />
            </span>
            <div>
              <p className="text-sm text-ink-secondary">Webhooks</p>
              <p className="text-2xl font-semibold text-ink-primary">5 endpoints</p>
            </div>
          </div>
        </CreamCard>
        <CreamCard hover className="p-5">
          <div className="flex items-center gap-3">
            <span className="rounded-xl bg-accent-amber-soft p-2.5">
              <Gauge className="h-5 w-5 text-accent-amber" />
            </span>
            <div>
              <p className="text-sm text-ink-secondary">Rate limit headroom</p>
              <p className="text-2xl font-semibold text-ink-primary">62%</p>
            </div>
          </div>
        </CreamCard>
      </div>

      <CreamCard className="mt-6 overflow-hidden">
        <div className="flex items-center justify-between border-b border-cream-border px-5 py-4">
          <h2 className="font-semibold text-ink-primary">API keys</h2>
          <button type="button" className="hq-btn-primary">
            Create key
          </button>
        </div>
        <table className="w-full text-left text-sm">
          <thead className="bg-cream-muted text-ink-secondary">
            <tr>
              <th className="px-5 py-3 font-medium">Name</th>
              <th className="px-5 py-3 font-medium">Prefix</th>
              <th className="px-5 py-3 font-medium">Scope</th>
              <th className="px-5 py-3 font-medium">Status</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-cream-border bg-white">
            {KEYS.map((k) => (
              <tr key={k.name}>
                <td className="px-5 py-3 font-medium text-ink-primary">{k.name}</td>
                <td className="px-5 py-3 font-mono text-xs text-ink-secondary">{k.prefix}</td>
                <td className="px-5 py-3 text-ink-secondary">{k.scope}</td>
                <td className="px-5 py-3">
                  <span className="rounded-md bg-accent-emerald-soft px-2 py-0.5 text-xs font-medium text-accent-emerald">
                    {k.status}
                  </span>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </CreamCard>

      <CreamCard className="mt-6 p-5">
        <h2 className="font-semibold text-ink-primary">Webhook endpoint</h2>
        <p className="mt-1 text-sm text-ink-secondary">Primary delivery URL for alert & telemetry fan-out.</p>
        <input
          readOnly
          value="https://hooks.next-iot.example/v1/tenant/acme/events"
          className="mt-4 w-full rounded-xl border border-cream-border bg-cream-alt px-4 py-3 font-mono text-xs text-ink-secondary"
        />
      </CreamCard>
    </HqPageContent>
  );
}
