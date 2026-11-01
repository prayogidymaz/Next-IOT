"use client";

import { useState } from "react";

import { HqPageContent } from "@/components/hq/HqPageContent";
import { getStudioMetaSync } from "@/lib/hq/studio-meta";
import { Badge } from "@/src/components/ui/badge";

import { AutomationStudioCanvas } from "./automation/AutomationStudioCanvas";
import { MeshWorkflowCanvas } from "./mesh/MeshWorkflowCanvas";

type StudioTab = "edge" | "mesh";

const meta = getStudioMetaSync("automation");

export function AutomationStudioBuilder() {
  const [tab, setTab] = useState<StudioTab>("edge");

  return (
    <HqPageContent>
      <div className="mb-6 flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
        <div className="flex w-fit gap-2 rounded-2xl border border-border bg-card p-1">
          <button
            type="button"
            className={`rounded-xl px-4 py-2 text-sm font-medium ${tab === "edge" ? "bg-muted text-foreground" : "text-muted-foreground"}`}
            onClick={() => setTab("edge")}
          >
            Edge Automations
          </button>
          <button
            type="button"
            className={`rounded-xl px-4 py-2 text-sm font-medium ${tab === "mesh" ? "bg-muted text-foreground" : "text-muted-foreground"}`}
            onClick={() => setTab("mesh")}
          >
            Mesh Workflows
          </button>
        </div>

        <div className="flex flex-wrap items-center gap-4 text-sm">
          <span className="text-muted-foreground">
            Devices: <span className="font-semibold text-foreground">{meta.deviceCount}</span>
          </span>
          <span className="text-muted-foreground">
            Pipelines: <span className="font-semibold text-foreground">{meta.pipelineCount}</span>
          </span>
          <Badge variant="outline" className="gap-1.5">
            <span className="h-2 w-2 animate-pulse rounded-full bg-green-500" aria-hidden />
            Sync {meta.lastSync}
          </Badge>
        </div>
      </div>

      {tab === "edge" ? <AutomationStudioCanvas /> : <MeshWorkflowCanvas />}
    </HqPageContent>
  );
}
