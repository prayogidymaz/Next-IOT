import { FirmwareReleasesPanel } from "@/components/firmware/FirmwareReleasesPanel";
import { HqPageContent } from "@/components/hq/HqPageContent";

export default function FirmwareReleasesPage() {
  return (
    <HqPageContent description="Upload firmware binaries, publish OTA rollouts, and track per-device status.">
      <FirmwareReleasesPanel />
    </HqPageContent>
  );
}
