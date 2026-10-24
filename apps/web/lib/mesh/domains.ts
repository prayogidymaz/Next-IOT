import type { DeviceResponse } from "@/lib/api/devices-schemas";

export const MESH_DOMAINS = [
  "sensor",
  "vision",
  "motion",
  "actuator",
  "security",
  "ui",
] as const;

export type MeshDomainId = (typeof MESH_DOMAINS)[number];

export const MESH_DOMAIN_COLORS: Record<MeshDomainId, { stroke: string; fill: string; log: string }> = {
  sensor: { stroke: "#2563EB", fill: "#DBEAFE", log: "text-blue-600" },
  vision: { stroke: "#EA580C", fill: "#FFEDD5", log: "text-orange-600" },
  motion: { stroke: "#DC2626", fill: "#FEE2E2", log: "text-red-600" },
  actuator: { stroke: "#16A34A", fill: "#DCFCE7", log: "text-green-600" },
  security: { stroke: "#B23A3A", fill: "#FEE2E2", log: "text-[#B23A3A]" },
  ui: { stroke: "#78716C", fill: "#F5EFE0", log: "text-stone-600" },
};

export function meshDomainFromDevice(device: DeviceResponse): MeshDomainId {
  const hay = `${device.device_type} ${device.device_category} ${device.name}`.toLowerCase();
  if (hay.includes("cctv") || hay.includes("camera") || hay.includes("vision")) return "vision";
  if (hay.includes("drone") || hay.includes("motion")) return "motion";
  if (hay.includes("sprayer") || hay.includes("valve") || hay.includes("gate") || hay.includes("actuator")) {
    return "actuator";
  }
  if (hay.includes("watch") || hay.includes("cyberdeck") || hay.includes("ui")) return "ui";
  if (hay.includes("alarm") || hay.includes("security") || hay.includes("intrusion")) return "security";
  return "sensor";
}

export function radialPosition(index: number, total: number, radius: number): { x: number; y: number } {
  if (total <= 0) return { x: 0, y: 0 };
  const angle = (2 * Math.PI * index) / total - Math.PI / 2;
  return { x: Math.cos(angle) * radius, y: Math.sin(angle) * radius };
}
