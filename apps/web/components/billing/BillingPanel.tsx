"use client";

import { useEffect, useState } from "react";

import { fetchBillingSubscription, fetchBillingUsage } from "@/lib/api/billing";
import { Card, CardContent, CardHeader, CardTitle } from "@/src/components/ui/card";

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
      <Card>
        <CardHeader>
          <CardTitle>Current plan</CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          {sub ? (
            <p className="text-sm text-foreground">
              <span className="font-medium">{sub.plan_name}</span> — {sub.status}
              {sub.trial_ends_at ? (
                <span className="ml-2 text-muted-foreground">Trial until {new Date(sub.trial_ends_at).toLocaleDateString()}</span>
              ) : null}
            </p>
          ) : (
            <p className="text-sm text-muted-foreground">Unable to load subscription</p>
          )}
        </CardContent>
      </Card>
      <Card>
        <CardHeader>
          <CardTitle>Usage</CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          {usage ? (
            <ul className="space-y-2 text-sm text-foreground">
              <li>
                Devices: {usage.devices_used} / {usage.devices_limit ?? "∞"}
              </li>
              <li>
                Messages (month): {usage.messages_used} / {usage.messages_limit ?? "∞"}
              </li>
            </ul>
          ) : (
            <p className="text-sm text-muted-foreground">Unable to load usage</p>
          )}
        </CardContent>
      </Card>
    </div>
  );
}
