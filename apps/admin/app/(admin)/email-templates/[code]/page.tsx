import { AdminShell } from "@/components/AdminShell";
import { EmailTemplateEditor } from "@/components/console/EmailTemplateEditor";

export default async function Page({ params }: { params: Promise<{ code: string }> }) {
  const { code } = await params;
  return (
    <AdminShell title={`Template: ${code}`}>
      <EmailTemplateEditor code={code} />
    </AdminShell>
  );
}
