"use client";

import type { MeshEventRecord } from "@/lib/api/mesh-schemas";
import type { DeviceResponse } from "@/lib/api/devices-schemas";
import { MESH_DOMAIN_COLORS, meshDomainFromDevice } from "@/lib/mesh/domains";

type MeshNodeDetailProps = {
  device: DeviceResponse | null;
  recentEvents: MeshEventRecord[];
  chain: MeshEventRecord[];
  onClose: () => void;
};

export function MeshNodeDetail({ device, recentEvents, chain, onClose }: MeshNodeDetailProps) {
  if (!device) return null;
  const domain = meshDomainFromDevice(device);
  const colors = MESH_DOMAIN_COLORS[domain];

  return (
    <aside className="flex h-full flex-col rounded-2xl border border-cream-border bg-white p-4 shadow-card">
      <div className="flex items-start justify-between gap-2">
        <div>
          <p className="text-xs font-medium uppercase tracking-wide text-ink-secondary">Device node</p>
          <h2 className="text-lg font-semibold text-ink-primary">{device.name}</h2>
          <p className="text-xs text-ink-secondary">{device.device_type} · {device.status}</p>
        </div>
        <button type="button" className="hq-btn-soft text-xs" onClick={onClose}>Close</button>
      </div>
      <div
        className="mt-3 rounded-xl border px-3 py-2 text-sm"
        style={{ borderColor: colors.stroke, backgroundColor: colors.fill }}
      >
        Domain: <span className="font-medium">{domain}</span>
      </div>
      <section className="mt-4">
        <h3 className="text-sm font-semibold text-ink-primary">Capabilities</h3>
        <ul className="mt-2 list-disc pl-5 text-xs text-ink-secondary">
          <li>Category: {device.device_category}</li>
          {device.metadata.slice(0, 4).map((m) => (
            <li key={m.key}>{m.key}: {m.value}</li>
          ))}
        </ul>
      </section>
      <section className="mt-4 flex-1 overflow-hidden">
        <h3 className="text-sm font-semibold text-ink-primary">Recent events</h3>
        <ul className="mt-2 max-h-40 overflow-y-auto space-y-1 text-xs font-mono text-ink-secondary">
          {recentEvents.length === 0 ? (
            <li>No events in stream window</li>
          ) : (
            recentEvents.map((ev) => (
              <li key={ev.event_id}>{ev.domain}/{ev.event_type}</li>
            ))
          )}
        </ul>
      </section>
      {chain.length > 0 ? (
        <section className="mt-3 border-t border-cream-border pt-3">
          <h3 className="text-sm font-semibold text-ink-primary">Event chain</h3>
          <ul className="mt-2 space-y-1 text-xs font-mono">
            {chain.map((ev) => (
              <li key={ev.event_id} className="text-ink-secondary">
                {ev.event_type} · {ev.event_id.slice(0, 8)}
              </li>
            ))}
          </ul>
        </section>
      ) : null}
    </aside>
  );
}
