import { ErrorBoundary } from "@/src/components/ErrorBoundary";
import { WorkflowAnalyticsDashboard } from "@/src/features/workflow-analytics/WorkflowAnalyticsDashboard";

export default function WorkflowAnalyticsRoute() {
  return (
    <ErrorBoundary>
      <WorkflowAnalyticsDashboard />
    </ErrorBoundary>
  );
}
