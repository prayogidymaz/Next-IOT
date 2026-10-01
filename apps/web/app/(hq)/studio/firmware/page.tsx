import { FirmwareStudioPage } from "@/components/studio/FirmwareStudioPage";
import { StudioMetaStrip } from "@/components/studio/StudioMetaStrip";
import { StudioRouteShell } from "@/components/studio/StudioRouteShell";

export default function FirmwareStudioRoute() {
  return (
    <StudioRouteShell meta={<StudioMetaStrip slug="firmware" />}>
      <FirmwareStudioPage />
    </StudioRouteShell>
  );
}
