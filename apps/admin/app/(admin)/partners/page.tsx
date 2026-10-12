import { AdminShell } from "@/components/AdminShell";
import { AdminPlaceholder } from "@/components/console/AdminPlaceholder";

export default function Page() {
  return (
    <AdminShell title="Partners">
      <AdminPlaceholder title="Partners" description="Reseller and integration partner registry — placeholder until partner billing ships." />
    </AdminShell>
  );
}
