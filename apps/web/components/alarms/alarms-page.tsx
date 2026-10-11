"use client";

import { useCallback, useEffect, useState } from "react";

import { CreamCard } from "@/components/ui/CreamCard";
import { HqPageContent } from "@/components/hq/HqPageContent";
import { acknowledgeAlarm, listAlarms, resolveAlarm, type AlarmItem } from "@/lib/api/alarms";

function severityClass(severity: string): string {
  if (severity === "critical") return "bg-red-100 text-red-800";
  if (severity === "major") return "bg-orange-100 text-orange-800";
  if (severity === "minor") return "bg-yellow-100 text-yellow-900";
  if (severity === "warning") return "bg-blue-100 text-blue-800";
  return "bg-gray-100 text-gray-700";
}

export function AlarmsPage() {
  const [items, setItems] = useState<AlarmItem[]>([]);
  const [status, setStatus] = useState("active");
  const reload = useCallback(async () => {
    setItems(await listAlarms({ status }));
  }, [status]);

  useEffect(() => {
    void reload();
    const t = setInterval(() => void reload(), 10_000);
    return () => clearInterval(t);
  }, [reload]);

  return (
    <HqPageContent description="Alarm lifecycle — ack, resolve, history">
      <CreamCard className="p-4">
        <select className="rounded border px-2 py-1 text-sm" value={status} onChange={(e) => setStatus(e.target.value)}>
          <option value="active">Active</option>
          <option value="acknowledged">Acknowledged</option>
          <option value="resolved">Resolved</option>
          <option value="cleared">Cleared</option>
        </select>
        <table className="mt-4 w-full text-left text-sm">
          <thead>
            <tr className="border-b text-ink-secondary">
              <th className="py-2">Severity</th>
              <th>Title</th>
              <th>Status</th>
              <th>When</th>
              <th />
            </tr>
          </thead>
          <tbody>
            {items.map((row) => (
              <tr key={row.id} className="border-b border-cream-border/60">
                <td className="py-2">
                  <span className={`rounded px-2 py-0.5 text-xs ${severityClass(row.severity)}`}>{row.severity}</span>
                </td>
                <td>{row.title}</td>
                <td>{row.status}</td>
                <td className="text-xs">{new Date(row.occurred_at).toLocaleString()}</td>
                <td className="space-x-2 text-right text-xs">
                  {row.status === "active" ? (
                    <button type="button" className="text-accent-cobalt" onClick={() => void acknowledgeAlarm(row.id).then(reload)}>
                      Ack
                    </button>
                  ) : null}
                  {row.status === "acknowledged" ? (
                    <button type="button" className="text-accent-emerald" onClick={() => void resolveAlarm(row.id).then(reload)}>
                      Resolve
                    </button>
                  ) : null}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </CreamCard>
    </HqPageContent>
  );
}
