import React from "react";
import { render, screen, waitFor } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";

vi.mock("@/hooks/useMeshEventStream", () => ({
  useMeshEventStream: () => ({
    events: [],
    state: "live",
    eventsPerMin: 0,
    prepend: vi.fn(),
  }),
}));

vi.mock("@/lib/api/devices", () => ({
  listDevices: vi.fn().mockResolvedValue([]),
}));

vi.mock("@/lib/api/mesh", () => ({
  listMeshWorkflows: vi.fn().mockResolvedValue([]),
  listMeshEvents: vi.fn().mockResolvedValue([]),
  getMeshEventChain: vi.fn().mockResolvedValue([]),
  publishMeshEvent: vi.fn(),
  testMeshWorkflow: vi.fn(),
}));

vi.mock("@/components/mesh/MeshGraphView", () => ({
  MeshGraphView: () => <div data-testid="mesh-graph-view" />,
  MeshGraphFilters: () => <div data-testid="mesh-graph-filters" />,
}));

import MeshGraphPage from "@/app/(hq)/mesh/graph/page";

describe("MeshGraphPage", () => {
  it("mounts without error", async () => {
    render(<MeshGraphPage />);
    await waitFor(() => {
      expect(screen.getByText("Trigger Mock Event")).toBeInTheDocument();
      expect(screen.getByText("Terminal Feed")).toBeInTheDocument();
    });
  });
});
