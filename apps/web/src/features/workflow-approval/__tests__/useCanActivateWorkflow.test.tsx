import { renderHook, waitFor } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";

import { useCanActivateWorkflow } from "../useCanActivateWorkflow";

vi.mock("@/lib/api/workflowApproval", () => ({
  fetchApprovalPolicy: vi.fn(),
  fetchPendingApprovals: vi.fn(),
}));

describe("useCanActivateWorkflow", () => {
  it("allows activation when policy does not require approval", async () => {
    const { fetchApprovalPolicy, fetchPendingApprovals } = await import("@/lib/api/workflowApproval");
    vi.mocked(fetchApprovalPolicy).mockResolvedValue({
      tenant_id: "t1",
      require_approval_for_production: false,
      min_approvers: 1,
      approver_roles_json: [],
    });
    vi.mocked(fetchPendingApprovals).mockResolvedValue([]);
    const { result } = renderHook(() => useCanActivateWorkflow("wf-1"));
    await waitFor(() => expect(result.current.loading).toBe(false));
    expect(result.current.canActivate).toBe(true);
    expect(result.current.blockedReason).toBeNull();
  });

  it("blocks when policy requires approval and no pending", async () => {
    const { fetchApprovalPolicy, fetchPendingApprovals } = await import("@/lib/api/workflowApproval");
    vi.mocked(fetchApprovalPolicy).mockResolvedValue({
      tenant_id: "t1",
      require_approval_for_production: true,
      min_approvers: 1,
      approver_roles_json: ["tenant_admin"],
    });
    vi.mocked(fetchPendingApprovals).mockResolvedValue([]);
    const { result } = renderHook(() => useCanActivateWorkflow("wf-1"));
    await waitFor(() => expect(result.current.loading).toBe(false));
    expect(result.current.canActivate).toBe(false);
    expect(result.current.blockedReason).toMatch(/approved change request/i);
  });

  it("blocks with pending message when request is open", async () => {
    const { fetchApprovalPolicy, fetchPendingApprovals } = await import("@/lib/api/workflowApproval");
    vi.mocked(fetchApprovalPolicy).mockResolvedValue({
      tenant_id: "t1",
      require_approval_for_production: true,
      min_approvers: 1,
      approver_roles_json: [],
    });
    vi.mocked(fetchPendingApprovals).mockResolvedValue([
      {
        id: "r1",
        workflow_id: "wf-1",
        requested_by: "u1",
        requested_at: "2026-01-01",
        status: "pending",
        notes: "",
        approved_by: null,
        approved_at: null,
        approval_notes: null,
      },
    ]);
    const { result } = renderHook(() => useCanActivateWorkflow("wf-1"));
    await waitFor(() => expect(result.current.loading).toBe(false));
    expect(result.current.canActivate).toBe(false);
    expect(result.current.blockedReason).toMatch(/pending review/i);
  });
});
