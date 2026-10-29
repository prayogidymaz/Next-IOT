import { render, screen, waitFor } from "@testing-library/react";
import { describe, expect, it, vi, beforeEach } from "vitest";

import { VersionHistory } from "../VersionHistory";

vi.mock("@/hooks/useHqToast", () => ({
  useHqToast: () => ({ showToast: vi.fn(), clearToast: vi.fn(), toast: null }),
}));

vi.mock("@/lib/api/workflowVersioning", () => ({
  fetchWorkflowVersions: vi.fn(async () => [
    {
      id: "a1",
      workflow_id: "wf-1",
      version_number: 2,
      snapshot_json: {},
      created_by: "user-1",
      created_at: "2026-01-01T00:00:00Z",
      is_active: true,
      parent_version_id: null,
    },
    {
      id: "b2",
      workflow_id: "wf-1",
      version_number: 1,
      snapshot_json: {},
      created_by: null,
      created_at: "2025-12-01T00:00:00Z",
      is_active: false,
      parent_version_id: null,
    },
  ]),
  rollbackWorkflowVersion: vi.fn(),
}));

describe("VersionHistory", () => {
  beforeEach(() => vi.clearAllMocks());

  it("renders heading and version rows", async () => {
    render(<VersionHistory workflowId="wf-1" />);
    expect(screen.getByText("Version history")).toBeTruthy();
    await waitFor(() => {
      expect(screen.getByText("v2")).toBeTruthy();
      expect(screen.getByText("v1")).toBeTruthy();
    });
  });

  it("shows active badge on current version", async () => {
    render(<VersionHistory workflowId="wf-1" />);
    await waitFor(() => expect(screen.getByText("Active")).toBeTruthy());
  });

  it("shows rollback on inactive version only", async () => {
    render(<VersionHistory workflowId="wf-1" />);
    await waitFor(() => {
      const rollbackButtons = screen.getAllByRole("button", { name: "Rollback" });
      expect(rollbackButtons.length).toBe(1);
    });
  });
});
