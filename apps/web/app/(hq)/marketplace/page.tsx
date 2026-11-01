import { HqPageShell } from "@/components/hq/HqPageShell";
import { MarketplaceListView } from "@/src/features/workflow-marketplace/MarketplaceListView";

export default function MarketplaceRoute() {
  return (
    <HqPageShell>
      <MarketplaceListView />
    </HqPageShell>
  );
}
