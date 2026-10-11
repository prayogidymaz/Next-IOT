import { AdminShell } from "@/components/AdminShell";
import { SuperAdminBillingPanel } from "@/components/console/SuperAdminBillingPanel";

export default function AdminBillingPage() {
  return (
    <AdminShell title="Billing">
      <SuperAdminBillingPanel />
    </AdminShell>
  );
}
