"use client";

import { useParams } from "next/navigation";

import { WorkflowCanvas } from "@/src/features/workflow-builder/WorkflowCanvas";

const API_BASE = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

export default function EditWorkflowPage() {
  const params = useParams<{ id: string }>();
  const token = typeof window !== "undefined" ? localStorage.getItem("access_token") ?? "" : "";
  return (
    <div className="p-6">
      <h1 className="mb-4 text-2xl font-semibold text-stone-900">Workflow {params.id}</h1>
      <WorkflowCanvas apiBase={API_BASE} token={token} workflowId={params.id} />
    </div>
  );
}
