import { AdminShell } from "@/components/AdminShell";
import { AdminPlaceholder } from "@/components/console/AdminPlaceholder";

export default function Page() {
  return (
    <AdminShell title="Email templates">
      <AdminPlaceholder title="Email templates" description="Manage transactional templates (welcome, invoice, alert). API wiring planned for next sprint." />
    </AdminShell>
  );
}
