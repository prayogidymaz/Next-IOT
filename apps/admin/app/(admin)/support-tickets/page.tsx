import { AdminShell } from "@/components/AdminShell";
import { SupportTicketsListPanel } from "@/components/console/Step9CAdminPanels";

export default function Page() {
  return (
    <AdminShell title="Support tickets">
      <SupportTicketsListPanel />
    </AdminShell>
  );
}
