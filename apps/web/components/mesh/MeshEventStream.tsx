"use client";

import { useMemo, useState } from "react";

import type { MeshEventRecord } from "@/lib/api/mesh-schemas";
import { MESH_DOMAIN_COLORS, MESH_DOMAINS, type MeshDomainId } from "@/lib/mesh/domains";

type MeshEventStreamProps = {
  events: MeshEventRecord[];
  paused: boolean;
  onPausedChange: (paused: boolean) => void;
  selectedEventId: string | null;
  onSelectEvent: (event: MeshEventRecord) => void;
  deviceNameById: Record<string, string>;
};

export function MeshEventStream({
  events,
  paused,
  onPausedChange,
  selectedEventId,
  onSelectEvent,
  deviceNameById,
}: MeshEventStreamProps) {
  const [domainFilter, setDomainFilter] = useState<MeshDomainId | "all">("all");
  const [typeFilter, setTypeFilter] = useState("");
  const [deviceFilter, setDeviceFilter] = useState("");

  const filtered = useMemo(() => {
    return events.filter((ev) => {
      if (domainFilter !== "all" && ev.domain !== domainFilter) return false;
      if (typeFilter && !ev.event_type.includes(typeFilter)) return false;
      if (deviceFilter && ev.device_id !== deviceFilter) return false;
      return true;
    });
  }, [events, domainFilter, typeFilter, deviceFilter]);

  const deviceOptions = useMemo(() => {
    const ids = new Set(events.map((e) => e.device_id));
    return [...ids];
  }, [events]);

  return (
    <div className="flex h-full min-h-[280px] flex-col rounded-2xl border border-cream-border bg-[#1a1a18] text-[#F5EFE0] shadow-card">
      <div className="flex flex-wrap items-center gap-2 border-b border-white/10 px-3 py-2">
        <span className="font-mono text-xs uppercase tracking-wider text-[#F5EFE0]/80">Terminal Feed</span>
        <button
          type="button"
          className="ml-auto rounded-lg border border-white/20 px-2 py-1 text-xs hover:bg-white/10"
          onClick={() => onPausedChange(!paused)}
        >
          {paused ? "Resume" : "Pause"}
        </button>
        <select
          className="rounded-lg border border-white/20 bg-transparent px-2 py-1 text-xs"
          value={domainFilter}
          onChange={(e) => setDomainFilter(e.target.value as MeshDomainId | "all")}
        >
          <option value="all">All domains</option>
          {MESH_DOMAINS.map((d) => (
            <option key={d} value={d}>{d}</option>
          ))}
        </select>
        <input
          className="w-28 rounded-lg border border-white/20 bg-transparent px-2 py-1 text-xs"
          placeholder="event_type"
          value={typeFilter}
          onChange={(e) => setTypeFilter(e.target.value)}
        />
        <select
          className="max-w-[140px] rounded-lg border border-white/20 bg-transparent px-2 py-1 text-xs"
          value={deviceFilter}
          onChange={(e) => setDeviceFilter(e.target.value)}
        >
          <option value="">All devices</option>
          {deviceOptions.map((id) => (
            <option key={id} value={id}>{deviceNameById[id] ?? id.slice(0, 8)}</option>
          ))}
        </select>
      </div>
      <div className="flex-1 overflow-y-auto p-2 font-mono text-[11px] leading-relaxed">
        {filtered.length === 0 ? (
          <p className="text-white/50">Waiting for mesh events…</p>
        ) : (
          filtered.map((ev) => {
            const colors = MESH_DOMAIN_COLORS[ev.domain];
            const active = selectedEventId === ev.event_id;
            return (
              <button
                key={ev.event_id}
                type="button"
                onClick={() => onSelectEvent(ev)}
                className={`mb-1 block w-full rounded px-2 py-1 text-left hover:bg-white/5 ${active ? "bg-white/10" : ""}`}
              >
                <span className="text-white/40">{new Date(ev.timestamp).toLocaleTimeString()}</span>
                <span className={`ml-2 ${colors.log}`}>[{ev.domain}]</span>
                <span className="ml-2 text-white">{ev.event_type}</span>
                <span className="ml-2 text-white/50">{deviceNameById[ev.device_id] ?? ev.device_id.slice(0, 8)}</span>
              </button>
            );
          })
        )}
      </div>
    </div>
  );
}
