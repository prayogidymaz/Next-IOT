import { AdminShell } from "@/components/AdminShell";
import { PartnersListPanel } from "@/components/console/Step9CAdminPanels";

export default function Page() {
  return (
    <AdminShell title="Partners">
      <PartnersListPanel />
    </AdminShell>
  );
}
