"use client";

import { useMemo, useState } from "react";

import { publishMeshEvent, testMeshWorkflow } from "@/lib/api/mesh";
import type { MeshWorkflowRecord } from "@/lib/api/mesh-schemas";
import type { DeviceResponse } from "@/lib/api/devices-schemas";
import { MOCK_MESH_EVENT_CATALOG } from "@/lib/mesh/mock-event-catalog";

type SimulationPlaygroundProps = {
  devices: DeviceResponse[];
  workflows: MeshWorkflowRecord[];
  onEventPublished: () => void;
};

export function SimulationPlayground({ devices, workflows, onEventPublished }: SimulationPlaygroundProps) {
  const [specId, setSpecId] = useState(MOCK_MESH_EVENT_CATALOG[0]?.id ?? "");
  const [deviceId, setDeviceId] = useState("");
  const [status, setStatus] = useState<string | null>(null);
  const [preview, setPreview] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  const spec = useMemo(
    () => MOCK_MESH_EVENT_CATALOG.find((s) => s.id === specId) ?? MOCK_MESH_EVENT_CATALOG[0],
    [specId],
  );

  const effectiveDeviceId = deviceId || devices[0]?.id || "";

  const triggerMock = async () => {
    if (!spec || !effectiveDeviceId) {
      setStatus("Pilih device terlebih dahulu.");
      return;
    }
    setLoading(true);
    setStatus(null);
    setPreview(null);
    try {
      const published = await publishMeshEvent({
        device_id: effectiveDeviceId,
        domain: spec.domain,
        event_type: spec.event_type,
        payload: spec.payload,
      });
      setStatus(`Published ${published.event_id.slice(0, 8)}…`);
      onEventPublished();

      const sampleEvent: Record<string, unknown> = {
        domain: spec.domain,
        event_type: spec.event_type,
        payload: spec.payload,
        device_id: effectiveDeviceId,
      };
      const lines: string[] = [];
      for (const wf of workflows.filter((w) => w.enabled)) {
        try {
          const dry = await testMeshWorkflow(wf.id, sampleEvent);
          lines.push(
            `${wf.name}: ${dry.conditions_passed ? "would run" : "skip"} (${dry.planned_actions.length} actions)`,
          );
        } catch {
          lines.push(`${wf.name}: test unavailable`);
        }
      }
      setPreview(lines.join("\n") || "No enabled workflows to preview.");
    } catch (err) {
      setStatus(err instanceof Error ? err.message : "Trigger failed");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="rounded-2xl border border-cream-border bg-white p-4 shadow-card">
      <h2 className="text-sm font-semibold text-ink-primary">Simulation playground</h2>
      <p className="mt-1 text-xs text-ink-secondary">POST /api/v1/mesh/events — test workflows tanpa hardware.</p>
      <label className="mt-3 block text-xs font-medium text-ink-secondary">
        Event type
        <select
          className="mt-1 w-full rounded-xl border border-cream-border px-2 py-2 text-sm"
          value={specId}
          onChange={(e) => setSpecId(e.target.value)}
        >
          {MOCK_MESH_EVENT_CATALOG.map((item) => (
            <option key={item.id} value={item.id}>{item.label}</option>
          ))}
        </select>
      </label>
      <label className="mt-3 block text-xs font-medium text-ink-secondary">
        Source device
        <select
          className="mt-1 w-full rounded-xl border border-cream-border px-2 py-2 text-sm"
          value={effectiveDeviceId}
          onChange={(e) => setDeviceId(e.target.value)}
        >
          {devices.map((d) => (
            <option key={d.id} value={d.id}>{d.name}</option>
          ))}
        </select>
      </label>
      <button
        type="button"
        className="hq-btn-primary mt-4 w-full text-sm disabled:opacity-60"
        disabled={loading}
        onClick={() => void triggerMock()}
      >
        Trigger Mock Event
      </button>
      {status ? <p className="mt-2 text-xs text-ink-secondary">{status}</p> : null}
      {preview ? (
        <pre className="mt-3 max-h-40 overflow-auto rounded-xl bg-cream-alt p-2 text-[11px] text-ink-secondary whitespace-pre-wrap">
          {preview}
        </pre>
      ) : null}
    </div>
  );
}
