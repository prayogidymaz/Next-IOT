import { AdminShell } from "@/components/AdminShell";
import { AdminPlaceholder } from "@/components/console/AdminPlaceholder";

export default function Page() {
  return (
    <AdminShell title="Backup / restore">
      <AdminPlaceholder title="Backup & restore" description="Trigger Postgres snapshots and restore drills from infrastructure runbooks." />
    </AdminShell>
  );
}
