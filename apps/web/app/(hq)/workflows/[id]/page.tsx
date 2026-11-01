"use client";

import { useParams } from "next/navigation";
import { useEffect, useState } from "react";

import { HqPageShell } from "@/components/hq/HqPageShell";
import { ApprovalRequestModal } from "@/src/features/workflow-approval/ApprovalRequestModal";
import { WorkflowActivateButton } from "@/src/features/workflow-approval/WorkflowActivateButton";
import { PublishTemplateModal } from "@/src/features/workflow-marketplace/PublishTemplateModal";
import { VersionHistory } from "@/src/features/workflow-versioning/VersionHistory";
import { WorkflowCanvas } from "@/src/features/workflow-builder/WorkflowCanvas";
import { getApiBaseUrl } from "@/lib/auth/api";
import { readApiAccessToken } from "@/lib/auth/api-headers";

const API_BASE = process.env.NEXT_PUBLIC_API_URL ?? getApiBaseUrl();

type TabId = "editor" | "history";

export default function EditWorkflowPage() {
  const params = useParams<{ id: string }>();
  const workflowId = params.id;
  const [token, setToken] = useState("");
  useEffect(() => {
    setToken(readApiAccessToken() ?? "");
  }, []);
  const [tab, setTab] = useState<TabId>("editor");
  const [approvalOpen, setApprovalOpen] = useState(false);
  const [publishOpen, setPublishOpen] = useState(false);
  const [enabled, setEnabled] = useState(false);

  useEffect(() => {
    if (!workflowId || !token) return;
    void fetch(`${API_BASE}/api/v1/mesh/workflows/${workflowId}`, {
      headers: { Authorization: `Bearer ${token}` },
    })
      .then((r) => (r.ok ? r.json() : null))
      .then((data: { enabled?: boolean } | null) => {
        if (data && typeof data.enabled === "boolean") setEnabled(data.enabled);
      })
      .catch(() => undefined);
  }, [workflowId, token]);

  return (
    <HqPageShell
      action={
        <div className="flex flex-wrap items-center gap-2">
          <WorkflowActivateButton workflowId={workflowId} token={token} enabled={enabled} onToggled={setEnabled} />
          <button type="button" className="rounded-lg border border-border bg-card px-2 py-1 text-sm text-foreground" onClick={() => setApprovalOpen(true)}>
            Request approval
          </button>
          <button type="button" className="rounded-lg border border-border bg-card px-2 py-1 text-sm text-foreground" onClick={() => setPublishOpen(true)}>
            Publish to Marketplace
          </button>
        </div>
      }
    >

      <div className="mb-4 flex gap-2 border-b border-border">
        {(["editor", "history"] as const).map((t) => (
          <button
            key={t}
            type="button"
            className={`border-b-2 px-3 py-2 text-sm capitalize ${tab === t ? "border-foreground font-medium text-foreground" : "border-transparent text-muted-foreground"}`}
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

      <ApprovalRequestModal workflowId={workflowId} open={approvalOpen} onClose={() => setApprovalOpen(false)} />
      <PublishTemplateModal workflowId={workflowId} open={publishOpen} onClose={() => setPublishOpen(false)} />
    </HqPageShell>
  );
}
