import { render, screen, waitFor } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";

import { MarketplaceListView } from "@/src/features/workflow-marketplace/MarketplaceListView";

vi.mock("next/link", () => ({
  default: ({ href, children }: { href: string; children: React.ReactNode }) => <a href={href}>{children}</a>,
}));

vi.mock("@/lib/api/workflowMarketplace", () => ({
  listMarketplaceTemplates: vi.fn(async () => [
    {
      id: "tpl-1",
      name: "Irrigation starter",
      description: "Auto irrigate on soil moisture",
      category: "irrigation",
      tags_json: [],
      author_tenant_id: "tenant-a",
      snapshot_json: {},
      downloads_count: 12,
      rating_avg: 4.5,
      rating_count: 2,
      published: true,
      created_at: "2026-01-01",
      locale: "id",
    },
  ]),
}));

describe("MarketplaceListView", () => {
  it("renders page title", async () => {
    render(<MarketplaceListView />);
    expect(screen.getByText("Template marketplace")).toBeTruthy();
  });

  it("lists template cards from API", async () => {
    render(<MarketplaceListView />);
    await waitFor(() => expect(screen.getByText("Irrigation starter")).toBeTruthy());
  });

  it("links to template detail", async () => {
    render(<MarketplaceListView />);
    await waitFor(() => {
      const link = screen.getByRole("link", { name: /Irrigation starter/i });
      expect(link.getAttribute("href")).toBe("/marketplace/tpl-1");
    });
  });
});
