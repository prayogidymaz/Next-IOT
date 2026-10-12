import { AdminShell } from "@/components/AdminShell";
import { PlatformSettingsPanel } from "@/components/console/PlatformSettingsPanel";

export default function Page() {
  return (
    <AdminShell title="Platform settings">
      <PlatformSettingsPanel />
    </AdminShell>
  );
}
