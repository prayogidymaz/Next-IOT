"use client";

import { useEffect, useState } from "react";

import { HqPageShell } from "@/components/hq/HqPageShell";
import { Button } from "@/components/ui/button";
import { listDeviceGroups, syncGroupConfig, type DeviceGroup } from "@/lib/api/fleet";

export default function FleetSyncPage() {
  const [groups, setGroups] = useState<DeviceGroup[]>([]);
  const [groupId, setGroupId] = useState("");
  const [progress, setProgress] = useState<{ targeted: number; acked: number; ack_rate: number } | null>(null);
  const [busy, setBusy] = useState(false);

  useEffect(() => {
    void listDeviceGroups().then((list) => {
      setGroups(list);
      if (list[0]) setGroupId(list[0].id);
    });
  }, []);

  async function runSync() {
    if (!groupId) return;
    setBusy(true);
    setProgress(null);
    try {
      const res = await syncGroupConfig(groupId, { interval_sec: 60 });
      setProgress(res);
    } finally {
      setBusy(false);
    }
  }

  return (
    <HqPageShell>
      <div className="max-w-md space-y-3 rounded-xl border border-border bg-card p-4 text-sm">
        <label className="block">
          Device group
          <select className="mt-1 w-full rounded border border-border bg-background px-2 py-1" value={groupId} onChange={(e) => setGroupId(e.target.value)}>
            {groups.map((g) => (
              <option key={g.id} value={g.id}>
                {g.name}
              </option>
            ))}
          </select>
        </label>
        <Button type="button" disabled={busy || !groupId} onClick={() => void runSync()}>
          Push config via MQTT
        </Button>
        {progress ? (
          <div className="space-y-2">
            <div className="h-2 overflow-hidden rounded-full bg-muted">
              <div className="h-full bg-primary transition-all" style={{ width: `${Math.round(progress.ack_rate * 100)}%` }} />
            </div>
            <p className="text-muted-foreground">
              Targeted {progress.targeted} · ACK {progress.acked} ({(progress.ack_rate * 100).toFixed(0)}%)
            </p>
          </div>
        ) : null}
      </div>
    </HqPageShell>
  );
}
