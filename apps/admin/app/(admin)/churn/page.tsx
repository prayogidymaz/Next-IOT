import { AdminShell } from "@/components/AdminShell";
import { ChurnPanel } from "@/components/console/SuperAdminExtendedPanels";

export default function Page() {
  return (
    <AdminShell title="Churn analysis">
      <ChurnPanel />
    </AdminShell>
  );
}
