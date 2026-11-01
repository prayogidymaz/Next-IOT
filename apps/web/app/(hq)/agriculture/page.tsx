import { SmartAgricultureDashboard } from "@/components/agriculture/SmartAgricultureDashboard";
import { HqPageShell } from "@/components/hq/HqPageShell";

export default function AgricultureHubPage() {
  return (
    <HqPageShell>
      <SmartAgricultureDashboard />
    </HqPageShell>
  );
}
