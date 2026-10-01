import { AutomationStudioBuilder } from "@/components/studio/AutomationStudioBuilder";
import { StudioMetaStrip } from "@/components/studio/StudioMetaStrip";
import { StudioRouteShell } from "@/components/studio/StudioRouteShell";

export default function AutomationStudioPage() {
  return (
    <StudioRouteShell meta={<StudioMetaStrip slug="automation" />}>
      <AutomationStudioBuilder />
    </StudioRouteShell>
  );
}
