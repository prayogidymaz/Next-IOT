import { AdminShell } from "@/components/AdminShell";
import { PlatformSettingsPanel } from "@/components/console/SuperAdminExtendedPanels";

export default function Page() {
  return (
    <AdminShell title="Platform settings">
      <PlatformSettingsPanel />
    </AdminShell>
  );
}
