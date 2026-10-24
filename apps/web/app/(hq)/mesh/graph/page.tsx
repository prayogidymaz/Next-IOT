"use client";

import { useCallback, useEffect, useMemo, useState } from "react";

import { MeshEventStream } from "@/components/mesh/MeshEventStream";
import { MeshGraphFilters, MeshGraphView } from "@/components/mesh/MeshGraphView";
import { MeshNodeDetail } from "@/components/mesh/MeshNodeDetail";
import { SimulationPlayground } from "@/components/mesh/SimulationPlayground";
import { HqPageContent } from "@/components/hq/HqPageContent";
import { listDevices } from "@/lib/api/devices";
import { getMeshEventChain, listMeshEvents, listMeshWorkflows } from "@/lib/api/mesh";
import type { MeshEventRecord } from "@/lib/api/mesh-schemas";
import type { MeshWorkflowRecord } from "@/lib/api/mesh-schemas";
import type { DeviceResponse } from "@/lib/api/devices-schemas";
import { useMeshEventStream } from "@/hooks/useMeshEventStream";
import type { MeshDomainId } from "@/lib/mesh/domains";

export default function MeshGraphPage() {
  const [devices, setDevices] = useState<DeviceResponse[]>([]);
  const [workflows, setWorkflows] = useState<MeshWorkflowRecord[]>([]);
  const [domainFilter, setDomainFilter] = useState<MeshDomainId | "all">("all");
  const [zoneFilter, setZoneFilter] = useState("");
  const [paused, setPaused] = useState(false);
  const [selectedDeviceId, setSelectedDeviceId] = useState<string | null>(null);
  const [selectedEvent, setSelectedEvent] = useState<MeshEventRecord | null>(null);
  const [chain, setChain] = useState<MeshEventRecord[]>([]);
  const [bootError, setBootError] = useState<string | null>(null);

  const { events, eventsPerMin, prepend } = useMeshEventStream(paused);

  const loadStatic = useCallback(async () => {
    try {
      const [devs, wfs, history] = await Promise.all([
        listDevices(),
        listMeshWorkflows(),
        listMeshEvents({ limit: 80 }),
      ]);
      setDevices(devs);
      setWorkflows(wfs);
      prepend(history);
      setBootError(null);
    } catch (err) {
      setBootError(err instanceof Error ? err.message : "Failed to load mesh graph");
    }
  }, [prepend]);

  useEffect(() => {
    void loadStatic();
  }, [loadStatic]);

  useEffect(() => {
    if (!selectedEvent) {
      setChain([]);
      return;
    }
    void getMeshEventChain(selectedEvent.event_id)
      .then(setChain)
      .catch(() => setChain([]));
  }, [selectedEvent]);

  const deviceNameById = useMemo(() => {
    const map: Record<string, string> = {};
    for (const d of devices) map[d.id] = d.name;
    return map;
  }, [devices]);

  const selectedDevice = devices.find((d) => d.id === selectedDeviceId) ?? null;
  const recentForDevice = useMemo(() => {
    if (!selectedDeviceId) return [];
    return events.filter((e) => e.device_id === selectedDeviceId).slice(0, 12);
  }, [events, selectedDeviceId]);

  const activeCount = useMemo(() => {
    const cutoff = Date.now() - 60_000;
    const ids = new Set(
      events.filter((e) => new Date(e.timestamp).getTime() >= cutoff).map((e) => e.device_id),
    );
    return ids.size;
  }, [events]);

  return (
    <HqPageContent description="Universal Mesh topology — cross-domain devices, live SSE event stream, and workflow simulation playground.">
      {bootError ? (
        <div className="rounded-xl border border-red-200 bg-red-50 px-3 py-2 text-sm text-red-700">{bootError}</div>
      ) : null}
      <MeshGraphFilters
        domainFilter={domainFilter}
        onDomainFilter={setDomainFilter}
        zoneFilter={zoneFilter}
        onZoneFilter={setZoneFilter}
        stats={{ nodes: devices.length, active: activeCount, eventsPerMin }}
      />
      <div className="grid gap-4 xl:grid-cols-[1fr_320px]">
        <div className="space-y-4">
          <MeshGraphView
            devices={devices}
            events={events}
            domainFilter={domainFilter}
            zoneFilter={zoneFilter}
            selectedDeviceId={selectedDeviceId}
            onSelectDevice={setSelectedDeviceId}
          />
          <MeshEventStream
            events={events}
            paused={paused}
            onPausedChange={setPaused}
            selectedEventId={selectedEvent?.event_id ?? null}
            onSelectEvent={(ev) => {
              setSelectedEvent(ev);
              setSelectedDeviceId(ev.device_id);
            }}
            deviceNameById={deviceNameById}
          />
        </div>
        <div className="space-y-4">
          <SimulationPlayground
            devices={devices}
            workflows={workflows}
            onEventPublished={() => void loadStatic()}
          />
          {selectedDevice || selectedEvent ? (
            <MeshNodeDetail
              device={selectedDevice}
              recentEvents={recentForDevice}
              chain={selectedEvent ? chain : []}
              onClose={() => {
                setSelectedDeviceId(null);
                setSelectedEvent(null);
              }}
            />
          ) : null}
        </div>
      </div>
    </HqPageContent>
  );
}
