import type { MeshDomainId } from "@/lib/mesh/domains";

export type MockMeshEventSpec = {
  id: string;
  label: string;
  domain: MeshDomainId;
  event_type: string;
  payload: Record<string, unknown>;
};

export const MOCK_MESH_EVENT_CATALOG: MockMeshEventSpec[] = [
  {
    id: "vision-motion",
    label: "Vision — motion_detected",
    domain: "vision",
    event_type: "motion_detected",
    payload: { confidence: 0.92, class: "motion" },
  },
  {
    id: "security-intrusion",
    label: "Security — intrusion_detected",
    domain: "security",
    event_type: "intrusion_detected",
    payload: { severity: "critical", zone: "plot_A" },
  },
  {
    id: "sensor-reading",
    label: "Sensor — reading_update",
    domain: "sensor",
    event_type: "reading_update",
    payload: { metrics: { temperature: 31.2, humidity: 78.1 } },
  },
  {
    id: "sensor-forecast",
    label: "Sensor — weather_forecast",
    domain: "sensor",
    event_type: "weather_forecast",
    payload: { rain_probability: 0.81, forecast: "rain_likely" },
  },
  {
    id: "actuator-state",
    label: "Actuator — state_changed",
    domain: "actuator",
    event_type: "state_changed",
    payload: { valve_open: true, tank_level_percent: 42 },
  },
  {
    id: "ui-ack",
    label: "UI — user_acknowledged",
    domain: "ui",
    event_type: "user_acknowledged",
    payload: { alert_id: "demo-alert" },
  },
];
