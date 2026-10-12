import { AdminShell } from "@/components/AdminShell";
import { RevenueAnalyticsPanel } from "@/components/console/SuperAdminExtendedPanels";

export default function Page() {
  return (
    <AdminShell title="Revenue analytics">
      <RevenueAnalyticsPanel />
    </AdminShell>
  );
}
