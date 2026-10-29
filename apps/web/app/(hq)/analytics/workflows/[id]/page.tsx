"use client";

import { useParams } from "next/navigation";

import { WorkflowAnalyticsDetail } from "@/src/features/workflow-analytics/WorkflowAnalyticsDetail";

export default function WorkflowAnalyticsDetailRoute() {
  const params = useParams<{ id: string }>();
  return <WorkflowAnalyticsDetail workflowId={params.id} />;
}
