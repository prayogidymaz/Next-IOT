import { render, screen } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";

import { MeshEventStream } from "@/components/mesh/MeshEventStream";
import type { MeshEventRecord } from "@/lib/api/mesh-schemas";

const sampleEvent: MeshEventRecord = {
  event_id: "11111111-1111-4111-8111-111111111111",
  tenant_id: "22222222-2222-4222-8222-222222222222",
  device_id: "33333333-3333-4333-8333-333333333333",
  domain: "vision",
  event_type: "motion_detected",
  timestamp: new Date().toISOString(),
  payload: { confidence: 0.9 },
  context: { capabilities: [] },
  correlation_id: null,
  parent_event_id: null,
};

describe("MeshEventStream", () => {
  it("renders terminal feed and event line", () => {
    render(
      <MeshEventStream
        events={[sampleEvent]}
        paused={false}
        onPausedChange={vi.fn()}
        selectedEventId={null}
        onSelectEvent={vi.fn()}
        deviceNameById={{ [sampleEvent.device_id]: "CCTV-A" }}
      />,
    );
    expect(screen.getByText("Terminal Feed")).toBeInTheDocument();
    expect(screen.getByText("motion_detected")).toBeInTheDocument();
    expect(screen.getAllByText("CCTV-A").length).toBeGreaterThan(0);
  });
});
