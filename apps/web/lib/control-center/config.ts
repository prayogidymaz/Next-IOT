import type { HqDomainId } from "@/lib/hq/domains";

export type ActuatorDef = {
  id: string;
  label: string;
  zone: string;
  domain: HqDomainId;
};

export const CONTROL_CENTER_ACTUATORS: ActuatorDef[] = [
  { id: "aerator-main", label: "Aerator main", zone: "Biofloc A", domain: "smart-farming" },
  { id: "pump-feed", label: "Feed pump", zone: "Biofloc B", domain: "smart-farming" },
  { id: "hvac-lobby", label: "HVAC lobby", zone: "Living room", domain: "smart-home" },
  { id: "light-greenhouse", label: "Grow lights", zone: "Greenhouse 2", domain: "smart-farming" },
  { id: "deck-relay", label: "Mesh relay", zone: "Cyberdeck rack", domain: "cyberdeck" },
  { id: "drone-pad-light", label: "Landing pad lights", zone: "Pad 3", domain: "drone" },
  { id: "amr-charger", label: "AMR charger relay", zone: "Line 2", domain: "robotics" },
];

export type FleetMarker = {
  id: string;
  label: string;
  domain: HqDomainId;
  lat: number;
  lon: number;
};

export const INITIAL_FLEET: FleetMarker[] = [
  { id: "pond-a", label: "Pond node A", domain: "smart-farming", lat: -6.21, lon: 106.845 },
  { id: "deck-1", label: "Cyberdeck Alpha", domain: "cyberdeck", lat: -6.214, lon: 106.851 },
  { id: "uav-7", label: "UAV-7 patrol", domain: "drone", lat: -6.218, lon: 106.839 },
];
