import { AdminShell } from "@/components/AdminShell";
import { SuperAdminSystemPanel } from "@/components/console/SuperAdminSystemPanel";

export default function AdminSystemPage() {
  return (
    <AdminShell title="System health">
      <SuperAdminSystemPanel />
    </AdminShell>
  );
}
