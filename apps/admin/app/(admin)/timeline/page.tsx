import { AdminShell } from "@/components/AdminShell";
import { TimelinePanel } from "@/components/console/SuperAdminExtendedPanels";

export default function Page() {
  return (
    <AdminShell title="Activity timeline">
      <TimelinePanel />
    </AdminShell>
  );
}
