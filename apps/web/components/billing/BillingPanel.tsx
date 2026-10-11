"use client";

import { useEffect, useState } from "react";

import { CreamCard } from "@/components/ui/CreamCard";
import { fetchBillingSubscription, fetchBillingUsage } from "@/lib/api/billing";

export function BillingPanel() {
  const [sub, setSub] = useState<{ plan_name: string; status: string; trial_ends_at: string | null } | null>(null);
  const [usage, setUsage] = useState<{ devices_used: number; devices_limit: number | null; messages_used: number; messages_limit: number | null } | null>(null);

  useEffect(() => {
    void Promise.all([fetchBillingSubscription(), fetchBillingUsage()])
      .then(([s, u]) => {
        setSub(s);
        setUsage(u);
      })
      .catch(() => {
        setSub(null);
        setUsage(null);
      });
  }, []);

  return (
    <div className="space-y-6">
      <CreamCard title="Current plan">
        {sub ? (
          <p className="text-sm">
            <span className="font-medium">{sub.plan_name}</span> — {sub.status}
            {sub.trial_ends_at ? (
              <span className="ml-2 text-ink-secondary">Trial until {new Date(sub.trial_ends_at).toLocaleDateString()}</span>
            ) : null}
          </p>
        ) : (
          <p className="text-sm text-ink-secondary">Unable to load subscription</p>
        )}
      </CreamCard>
      <CreamCard title="Usage">
        {usage ? (
          <ul className="space-y-2 text-sm">
            <li>
              Devices: {usage.devices_used} / {usage.devices_limit ?? "∞"}
            </li>
            <li>
              Messages (month): {usage.messages_used} / {usage.messages_limit ?? "∞"}
            </li>
          </ul>
        ) : null}
      </CreamCard>
    </div>
  );
}
