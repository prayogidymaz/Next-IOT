import { HqPageShell } from "@/components/hq/HqPageShell";
import { ApprovalPolicyPage } from "@/src/features/workflow-approval/ApprovalPolicyPage";

export default function ApprovalPolicyRoute() {
  return (
    <HqPageShell>
      <ApprovalPolicyPage />
    </HqPageShell>
  );
}
