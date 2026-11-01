import { YieldForecastView } from "@/components/agriculture/YieldForecastView";
import { HqPageShell } from "@/components/hq/HqPageShell";

export default function AnalyticsYieldRoute() {
  return (
    <HqPageShell>
      <YieldForecastView />
    </HqPageShell>
  );
}
