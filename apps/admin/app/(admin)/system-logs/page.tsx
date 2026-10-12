import { AdminShell } from "@/components/AdminShell";
import { SystemLogsPanel } from "@/components/console/SuperAdminExtendedPanels";

export default function Page() {
  return (
    <AdminShell title="System logs">
      <SystemLogsPanel />
    </AdminShell>
  );
}
