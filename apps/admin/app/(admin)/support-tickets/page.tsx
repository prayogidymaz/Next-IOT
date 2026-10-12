import { AdminShell } from "@/components/AdminShell";
import { AdminPlaceholder } from "@/components/console/AdminPlaceholder";

export default function Page() {
  return (
    <AdminShell title="Support tickets">
      <AdminPlaceholder title="Support tickets" description="Track tenant support requests and SLA. Connect to helpdesk integration in a follow-up release." />
    </AdminShell>
  );
}
