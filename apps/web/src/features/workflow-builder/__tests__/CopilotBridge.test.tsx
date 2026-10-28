import { fireEvent, render, screen, waitFor } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";

import { CopilotBridge } from "../CopilotBridge";

describe("CopilotBridge", () => {
  it("applies mock API draft to canvas", async () => {
    const draft = {
      draft_id: "11111111-1111-4111-8111-111111111111",
      tenant_id: "22222222-2222-4222-8222-222222222222",
      locale: "id",
      name: "Test",
      description: "d",
      trigger: { kind: "sensor_threshold" as const, sensor: "soil_moisture", operator: "lt" as const, threshold: 40 },
      actions: [{ action: "open", actuator: "valve_A1", duration_minutes: 15 }],
      confidence: 0.9,
      source: "mock",
    };
    vi.stubGlobal(
      "fetch",
      vi.fn().mockResolvedValue({
        ok: true,
        json: async () => ({ draft }),
      }),
    );
    const onApply = vi.fn();
    render(<CopilotBridge apiBase="http://localhost:8000" token="t" onApply={onApply} />);
    fireEvent.click(screen.getByText("Generate from AI"));
    fireEvent.change(screen.getByPlaceholderText(/plot A/i), {
      target: { value: "kalau tanah kering siram 15 menit" },
    });
    fireEvent.click(screen.getByText("Preview"));
    await waitFor(() => {
      const btn = screen.getByText("Apply to canvas");
      expect(btn.hasAttribute("disabled")).toBe(false);
    });
    fireEvent.click(screen.getByText("Apply to canvas"));
    expect(onApply).toHaveBeenCalled();
    const appliedNodes = onApply.mock.calls[0]?.[0] as unknown[] | undefined;
    expect(appliedNodes?.length).toBeGreaterThan(0);
  });
});
