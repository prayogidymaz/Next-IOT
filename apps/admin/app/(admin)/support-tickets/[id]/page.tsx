import { AdminShell } from "@/components/AdminShell";
import { SupportTicketDetailPanel } from "@/components/console/Step9CAdminPanels";

type Props = { params: Promise<{ id: string }> };

export default async function Page({ params }: Props) {
  const { id } = await params;
  return (
    <AdminShell title="Support ticket">
      <SupportTicketDetailPanel ticketId={id} />
    </AdminShell>
  );
}
