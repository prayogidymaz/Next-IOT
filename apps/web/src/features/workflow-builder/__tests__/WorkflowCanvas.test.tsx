import { render, screen } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";

import { WorkflowCanvas } from "../WorkflowCanvas";

vi.mock("@xyflow/react", async () => {
  const actual = await vi.importActual<typeof import("@xyflow/react")>("@xyflow/react");
  return {
    ...actual,
    ReactFlow: ({ children }: { children?: React.ReactNode }) => <div data-testid="react-flow">{children}</div>,
    Background: () => null,
    Controls: () => null,
    useReactFlow: () => ({ screenToFlowPosition: (p: { x: number; y: number }) => p, fitView: () => undefined }),
  };
});

describe("WorkflowCanvas", () => {
  it("renders canvas toolbar", () => {
    render(<WorkflowCanvas apiBase="http://localhost:8000" token="test-token" />);
    expect(screen.getByText("Save")).toBeTruthy();
    expect(screen.getByText("Generate from AI")).toBeTruthy();
    expect(screen.getByTestId("react-flow")).toBeTruthy();
  });
});
