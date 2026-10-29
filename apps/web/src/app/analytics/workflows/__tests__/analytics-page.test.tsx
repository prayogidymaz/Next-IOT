import { render, screen, waitFor } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";

import { WorkflowAnalyticsDashboard } from "@/src/features/workflow-analytics/WorkflowAnalyticsDashboard";

vi.mock("next/link", () => ({
  default: ({ href, children }: { href: string; children: React.ReactNode }) => <a href={href}>{children}</a>,
}));

vi.mock("@/lib/api/workflowAnalytics", () => ({
  fetchTopFiredWorkflows: vi.fn(async () => [
    {
      workflow_id: "wf-99",
      name: "Night irrigation",
      fire_count: 40,
      success_count: 38,
      fail_count: 2,
      avg_duration_ms: 120,
      savings_idr_estimate: 50000,
    },
  ]),
}));

describe("WorkflowAnalyticsDashboard", () => {
  it("renders dashboard heading", () => {
    render(<WorkflowAnalyticsDashboard />);
    expect(screen.getByText("Workflow analytics")).toBeTruthy();
  });

  it("shows period selector buttons", () => {
    render(<WorkflowAnalyticsDashboard />);
    expect(screen.getByRole("button", { name: "7d" })).toBeTruthy();
    expect(screen.getByRole("button", { name: "30d" })).toBeTruthy();
  });

  it("loads top-fired table rows", async () => {
    render(<WorkflowAnalyticsDashboard />);
    await waitFor(() => {
      expect(screen.getByText("Night irrigation")).toBeTruthy();
      expect(screen.getByText("40")).toBeTruthy();
    });
  });
});
