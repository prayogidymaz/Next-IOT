"use client";

import {
  Background,
  BackgroundVariant,
  Controls,
  Handle,
  Position,
  ReactFlow,
  ReactFlowProvider,
  type Edge,
  type Node,
  type NodeProps,
} from "@xyflow/react";
import "@xyflow/react/dist/style.css";
import { useEffect, useMemo, useState } from "react";

import type { MeshEventRecord } from "@/lib/api/mesh-schemas";
import type { DeviceResponse } from "@/lib/api/devices-schemas";
import {
  MESH_DOMAIN_COLORS,
  MESH_DOMAINS,
  meshDomainFromDevice,
  radialPosition,
  type MeshDomainId,
} from "@/lib/mesh/domains";

type HubData = { label: string };
type DeviceNodeData = {
  label: string;
  domain: MeshDomainId;
  deviceId: string;
  active: boolean;
};

type MeshNode = Node<HubData | DeviceNodeData>;

function HubNode({ data }: NodeProps<Node<HubData>>) {
  return (
    <div className="rounded-full border-2 border-[#556B4A] bg-[#F5EFE0] px-6 py-4 text-center shadow-card">
      <Handle type="target" position={Position.Top} className="opacity-0" />
      <p className="text-xs font-medium uppercase tracking-wide text-[#556B4A]">Tenant hub</p>
      <p className="text-sm font-semibold text-ink-primary">{data.label}</p>
      <Handle type="source" position={Position.Bottom} className="opacity-0" />
    </div>
  );
}

function DeviceMeshNode({ data }: NodeProps<Node<DeviceNodeData>>) {
  const colors = MESH_DOMAIN_COLORS[data.domain];
  return (
    <div
      className="min-w-[120px] rounded-2xl border-2 px-3 py-2 text-center shadow-sm"
      style={{ borderColor: colors.stroke, backgroundColor: colors.fill }}
    >
      <Handle type="target" position={Position.Left} />
      <p className="text-[10px] uppercase text-ink-secondary">{data.domain}</p>
      <p className="text-xs font-semibold text-ink-primary">{data.label}</p>
      {data.active ? <span className="text-[10px] text-green-700">● live</span> : null}
      <Handle type="source" position={Position.Right} />
    </div>
  );
}

const nodeTypes = { hub: HubNode, device: DeviceMeshNode };

const EDGE_WINDOW_MS = 60_000;

function buildGraph(
  devices: DeviceResponse[],
  events: MeshEventRecord[],
  domainFilter: MeshDomainId | "all",
  zoneFilter: string,
): { nodes: MeshNode[]; edges: Edge[] } {
  const filteredDevices = devices.filter((d) => {
    const domain = meshDomainFromDevice(d);
    if (domainFilter !== "all" && domain !== domainFilter) return false;
    if (zoneFilter) {
      const zoneMeta = d.metadata.find((m) => m.key === "zone" || m.key === "physical_zone");
      if (zoneMeta && !zoneMeta.value.toLowerCase().includes(zoneFilter.toLowerCase())) return false;
    }
    return true;
  });

  const now = Date.now();
  const recent = events.filter((e) => now - new Date(e.timestamp).getTime() <= EDGE_WINDOW_MS);
  const activeIds = new Set(recent.map((e) => e.device_id));

  const nodes: MeshNode[] = [
    {
      id: "hub",
      type: "hub",
      position: { x: 320, y: 220 },
      data: { label: "Mesh center" },
      draggable: false,
    },
  ];

  filteredDevices.forEach((device, index) => {
    const pos = radialPosition(index, filteredDevices.length, 220);
    nodes.push({
      id: device.id,
      type: "device",
      position: { x: 320 + pos.x, y: 220 + pos.y },
      data: {
        label: device.name,
        domain: meshDomainFromDevice(device),
        deviceId: device.id,
        active: activeIds.has(device.id),
      },
    });
  });

  const edges: Edge[] = filteredDevices.map((device) => ({
    id: `hub-${device.id}`,
    source: "hub",
    target: device.id,
    animated: activeIds.has(device.id),
    style: { stroke: activeIds.has(device.id) ? "#556B4A" : "#d6d3d1" },
  }));

  const pairCounts = new Map<string, number>();
  for (const ev of recent) {
    const key = ev.device_id;
    pairCounts.set(key, (pairCounts.get(key) ?? 0) + 1);
  }
  const sorted = [...pairCounts.entries()].sort((a, b) => b[1] - a[1]).slice(0, 8);
  for (let i = 0; i < sorted.length - 1; i += 1) {
    const a = sorted[i]?.[0];
    const b = sorted[i + 1]?.[0];
    if (!a || !b) continue;
    edges.push({
      id: `peer-${a}-${b}`,
      source: a,
      target: b,
      animated: true,
      style: { stroke: "#D97757", strokeDasharray: "4 2" },
    });
  }

  return { nodes, edges };
}

type MeshGraphViewProps = {
  devices: DeviceResponse[];
  events: MeshEventRecord[];
  domainFilter: MeshDomainId | "all";
  zoneFilter: string;
  selectedDeviceId: string | null;
  onSelectDevice: (deviceId: string | null) => void;
};

function GraphInner({
  devices,
  events,
  domainFilter,
  zoneFilter,
  selectedDeviceId,
  onSelectDevice,
}: MeshGraphViewProps) {
  const graph = useMemo(
    () => buildGraph(devices, events, domainFilter, zoneFilter),
    [devices, events, domainFilter, zoneFilter],
  );
  const [nodes, setNodes] = useState(graph.nodes);
  const [edges, setEdges] = useState(graph.edges);

  useEffect(() => {
    setNodes(graph.nodes);
    setEdges(graph.edges);
  }, [graph]);

  return (
    <div className="h-[420px] overflow-hidden rounded-2xl border border-cream-border bg-cream-alt shadow-card">
      <ReactFlow
        nodes={nodes}
        edges={edges}
        nodeTypes={nodeTypes}
        fitView
        onNodeClick={(_, node) => {
          if (node.id === "hub") onSelectDevice(null);
          else onSelectDevice(node.id);
        }}
        proOptions={{ hideAttribution: true }}
      >
        <Background variant={BackgroundVariant.Dots} gap={18} size={1} color="#ECECE8" />
        <Controls className="!rounded-xl !border-cream-border !shadow-card" />
      </ReactFlow>
      {selectedDeviceId ? (
        <p className="border-t border-cream-border px-3 py-1 text-xs text-ink-secondary">
          Selected: {selectedDeviceId.slice(0, 8)}…
        </p>
      ) : null}
    </div>
  );
}

export function MeshGraphView(props: MeshGraphViewProps) {
  return (
    <ReactFlowProvider>
      <GraphInner {...props} />
    </ReactFlowProvider>
  );
}

export function MeshGraphFilters({
  domainFilter,
  onDomainFilter,
  zoneFilter,
  onZoneFilter,
  stats,
}: {
  domainFilter: MeshDomainId | "all";
  onDomainFilter: (v: MeshDomainId | "all") => void;
  zoneFilter: string;
  onZoneFilter: (v: string) => void;
  stats: { nodes: number; active: number; eventsPerMin: number };
}) {
  return (
    <div className="flex flex-wrap items-center gap-2">
      <span className="rounded-full bg-[#556B4A]/10 px-3 py-1 text-xs font-medium text-[#556B4A]">
        {stats.nodes} nodes · {stats.active} active · {stats.eventsPerMin} evt/min
      </span>
      <select
        className="rounded-xl border border-cream-border bg-white px-2 py-1 text-xs"
        value={domainFilter}
        onChange={(e) => onDomainFilter(e.target.value as MeshDomainId | "all")}
      >
        <option value="all">All domains</option>
        {MESH_DOMAINS.map((d) => (
          <option key={d} value={d}>{d}</option>
        ))}
      </select>
      <input
        className="rounded-xl border border-cream-border bg-white px-2 py-1 text-xs"
        placeholder="Zone filter"
        value={zoneFilter}
        onChange={(e) => onZoneFilter(e.target.value)}
      />
    </div>
  );
}
