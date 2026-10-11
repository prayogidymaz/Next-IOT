import { FirmwareStudioWizard } from "@/components/firmware/FirmwareStudioWizard";
import { HqPageContent } from "@/components/hq/HqPageContent";

export default function FirmwareStudioPage() {
  return (
    <HqPageContent description="Generate ESP32 PlatformIO projects from Device Profiles and the Next-IOT SDK.">
      <FirmwareStudioWizard />
    </HqPageContent>
  );
}
