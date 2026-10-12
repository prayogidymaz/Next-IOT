import { AdminShell } from "@/components/AdminShell";
import { EmailTemplatesListPanel } from "@/components/console/Step9CAdminPanels";

export default function Page() {
  return (
    <AdminShell title="Email templates">
      <EmailTemplatesListPanel />
    </AdminShell>
  );
}
