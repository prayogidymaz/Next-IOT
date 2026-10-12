import { AdminShell } from "@/components/AdminShell";
import { FinanceExportPanel } from "@/components/console/SuperAdminExtendedPanels";

export default function Page() {
  return (
    <AdminShell title="Finance export">
      <FinanceExportPanel />
    </AdminShell>
  );
}
