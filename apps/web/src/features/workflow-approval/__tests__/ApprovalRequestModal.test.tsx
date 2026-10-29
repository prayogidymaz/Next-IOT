import { fireEvent, render, screen, waitFor } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";

import { ApprovalRequestModal } from "../ApprovalRequestModal";

const showToast = vi.fn();

vi.mock("@/hooks/useHqToast", () => ({
  useHqToast: () => ({ showToast, clearToast: vi.fn(), toast: null }),
}));

vi.mock("@/lib/api/workflowApproval", () => ({
  requestWorkflowApproval: vi.fn(async () => ({ id: "req-1" })),
}));

describe("ApprovalRequestModal", () => {
  it("does not render when closed", () => {
    render(<ApprovalRequestModal workflowId="wf-1" open={false} onClose={() => undefined} />);
    expect(screen.queryByText("Request approval")).toBeNull();
  });

  it("renders notes field when open", () => {
    render(<ApprovalRequestModal workflowId="wf-1" open onClose={() => undefined} />);
    expect(screen.getByText("Request approval")).toBeTruthy();
    expect(screen.getByPlaceholderText(/Describe changes/)).toBeTruthy();
  });

  it("submits approval request", async () => {
    const onClose = vi.fn();
    const { requestWorkflowApproval } = await import("@/lib/api/workflowApproval");
    render(<ApprovalRequestModal workflowId="wf-1" open onClose={onClose} />);
    fireEvent.change(screen.getByPlaceholderText(/Describe changes/), { target: { value: "Ship to prod" } });
    fireEvent.click(screen.getByRole("button", { name: "Submit" }));
    await waitFor(() => {
      expect(requestWorkflowApproval).toHaveBeenCalledWith("wf-1", "Ship to prod");
      expect(showToast).toHaveBeenCalledWith("Approval request submitted", "success");
      expect(onClose).toHaveBeenCalled();
    });
  });
});
