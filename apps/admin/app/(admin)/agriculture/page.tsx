import { AdminShell } from "@/components/AdminShell";
import { AgriPlatformPanel } from "@/components/console/AgriAdminPanels";

export default function Page() {
  return (
    <AdminShell title="Agriculture vertical">
      <AgriPlatformPanel />
    </AdminShell>
  );
}
