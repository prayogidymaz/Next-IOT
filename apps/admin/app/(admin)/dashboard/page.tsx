import { AdminShell } from "@/components/AdminShell";
import { SuperAdminDashboard } from "@/components/console/SuperAdminDashboard";

export default function AdminDashboardPage() {
  return (
    <AdminShell title="Platform dashboard">
      <SuperAdminDashboard />
    </AdminShell>
  );
}
