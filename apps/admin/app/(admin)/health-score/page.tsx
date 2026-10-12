import { AdminShell } from "@/components/AdminShell";
import { HealthScorePanel } from "@/components/console/SuperAdminExtendedPanels";

export default function Page() {
  return (
    <AdminShell title="Customer health score">
      <HealthScorePanel />
    </AdminShell>
  );
}
