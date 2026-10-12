import { AdminShell } from "@/components/AdminShell";
import { ImpersonationAuditPanel } from "@/components/console/Step9CAdminPanels";

export default function Page() {
  return (
    <AdminShell title="Impersonation audit">
      <ImpersonationAuditPanel />
    </AdminShell>
  );
}
