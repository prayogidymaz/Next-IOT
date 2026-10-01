import { MissionStudioPage } from "@/components/studio/MissionStudioPage";
import { StudioMetaStrip } from "@/components/studio/StudioMetaStrip";
import { StudioRouteShell } from "@/components/studio/StudioRouteShell";

export default function MissionStudioRoute() {
  return (
    <StudioRouteShell meta={<StudioMetaStrip slug="missions" />}>
      <MissionStudioPage />
    </StudioRouteShell>
  );
}
