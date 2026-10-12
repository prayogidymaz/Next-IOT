import { AdminShell } from "@/components/AdminShell";
import { AuditLogPanel } from "@/components/console/SuperAdminExtendedPanels";

export default function Page() {
  return (
    <AdminShell title="Audit log">
      <AuditLogPanel />
    </AdminShell>
  );
}
