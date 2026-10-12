import { AdminShell } from "@/components/AdminShell";
import { BackupListPanel } from "@/components/console/Step9CAdminPanels";

export default function Page() {
  return (
    <AdminShell title="Backup / restore">
      <BackupListPanel />
    </AdminShell>
  );
}
