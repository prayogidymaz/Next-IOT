import { AdminShell } from "@/components/AdminShell";
import { AnnouncementsPanel } from "@/components/console/SuperAdminExtendedPanels";

export default function Page() {
  return (
    <AdminShell title="Announcements">
      <AnnouncementsPanel />
    </AdminShell>
  );
}
