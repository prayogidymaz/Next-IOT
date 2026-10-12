import { AdminShell } from "@/components/AdminShell";
import { AgriAnalyticsPanel } from "@/components/console/AgriAdminPanels";

export default function Page() {
  return (
    <AdminShell title="Agri platform analytics">
      <AgriAnalyticsPanel />
    </AdminShell>
  );
}
