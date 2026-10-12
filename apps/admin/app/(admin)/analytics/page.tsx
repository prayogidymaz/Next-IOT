import { AdminShell } from "@/components/AdminShell";
import { AnalyticsPanel } from "@/components/console/SuperAdminExtendedPanels";

export default function Page() {
  return (
    <AdminShell title="Analytics deep dive">
      <AnalyticsPanel />
    </AdminShell>
  );
}
