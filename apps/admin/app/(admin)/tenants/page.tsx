import { AdminShell } from "@/components/AdminShell";
import { SuperAdminTenantsPanel } from "@/components/console/SuperAdminTenantsPanel";

export default function AdminTenantsPage() {
  return (
    <AdminShell title="Tenants">
      <SuperAdminTenantsPanel />
    </AdminShell>
  );
}
