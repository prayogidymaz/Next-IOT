import { HqPageShell } from "@/components/hq/HqPageShell";
import { WorkflowsListView } from "@/components/workflows/WorkflowsListView";

export default function WorkflowsListPage() {
  return (
    <HqPageShell>
      <WorkflowsListView />
    </HqPageShell>
  );
}
