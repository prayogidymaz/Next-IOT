"use client";

import { useParams } from "next/navigation";
import { useState } from "react";

import { VersionHistory } from "@/src/features/workflow-versioning/VersionHistory";
import { WorkflowCanvas } from "@/src/features/workflow-builder/WorkflowCanvas";
import { getApiBaseUrl } from "@/lib/auth/api";

const API_BASE = process.env.NEXT_PUBLIC_API_URL ?? getApiBaseUrl();

type TabId = "editor" | "history";

export default function EditWorkflowPage() {
  const params = useParams<{ id: string }>();
  const workflowId = params.id;
  const token = typeof window !== "undefined" ? localStorage.getItem("access_token") ?? "" : "";
  const [tab, setTab] = useState<TabId>("editor");
  return (
    <div className="p-6">
      <div className="mb-4 flex flex-wrap items-center justify-between gap-3">
        <h1 className="text-2xl font-semibold text-stone-900">Workflow {workflowId}</h1>
      </div>

      <div className="mb-4 flex gap-2 border-b border-stone-200">
        {(["editor", "history"] as const).map((t) => (
          <button
            key={t}
            type="button"
            className={`border-b-2 px-3 py-2 text-sm capitalize ${tab === t ? "border-stone-900 font-medium" : "border-transparent text-stone-500"}`}
            onClick={() => setTab(t)}
          >
            {t === "editor" ? "Editor" : "History"}
          </button>
        ))}
      </div>

      {tab === "editor" ? (
        <WorkflowCanvas apiBase={API_BASE} token={token} workflowId={workflowId} />
      ) : (
        <VersionHistory workflowId={workflowId} />
      )}

    </div>
  );
}
