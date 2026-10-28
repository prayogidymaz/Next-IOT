import { describe, expect, it } from "vitest";

import { draftToFlow, flowToDefinitionPayload } from "../serializer";
import type { WorkflowDraft } from "../types";

const sampleDraft: WorkflowDraft = {
  draft_id: "11111111-1111-4111-8111-111111111111",
  tenant_id: "22222222-2222-4222-8222-222222222222",
  locale: "id",
  name: "Irrigation plot A",
  description: "Test",
  trigger: {
    kind: "sensor_threshold",
    sensor: "soil_moisture",
    operator: "lt",
    threshold: 40,
    device: "plot_A_sensor",
  },
  actions: [{ actuator: "valve_A1", action: "open", duration_minutes: 15 }],
  confidence: 0.9,
  source: "mock",
};

describe("serializer", () => {
  it("converts draft to nodes and edges", () => {
    const { nodes, edges } = draftToFlow(sampleDraft);
    expect(nodes.length).toBe(2);
    expect(edges.length).toBe(1);
    expect(nodes[0]?.data.kind).toBe("trigger");
  });

  it("exports mesh definition payload from flow", () => {
    const { nodes, edges } = draftToFlow(sampleDraft);
    const payload = flowToDefinitionPayload(nodes, edges, "test-flow");
    expect(payload.name).toBe("test-flow");
    expect(Array.isArray(payload.actions)).toBe(true);
  });
});
