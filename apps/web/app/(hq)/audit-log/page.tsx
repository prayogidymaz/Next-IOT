import { AuditLogPanel } from "@/components/audit/AuditLogPanel";
import { HqPageShell } from "@/components/hq/HqPageShell";

export default function AuditLogPage() {
  return (
    <HqPageShell>
      <AuditLogPanel />
    </HqPageShell>
  );
}
