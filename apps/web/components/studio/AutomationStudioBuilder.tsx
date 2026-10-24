"use client";

import { useState } from "react";

import { HqPageContent } from "@/components/hq/HqPageContent";

import { AutomationStudioCanvas } from "./automation/AutomationStudioCanvas";
import { MeshWorkflowCanvas } from "./mesh/MeshWorkflowCanvas";

type StudioTab = "edge" | "mesh";

export function AutomationStudioBuilder() {
  const [tab, setTab] = useState<StudioTab>("edge");

  return (
    <HqPageContent
      description={
        tab === "edge"
          ? "React Flow canvas — Trigger → Condition → Action with JSON import/export and property panel."
          : "Cross-domain mesh workflows — mesh_event triggers, device resolver, dispatch, and wait steps."
      }
    >
      <div className="mb-4 flex gap-2 rounded-2xl border border-cream-border bg-white p-1 w-fit">
        <button
          type="button"
          className={`rounded-xl px-4 py-2 text-sm font-medium ${tab === "edge" ? "bg-cream-alt text-ink-primary" : "text-ink-secondary"}`}
          onClick={() => setTab("edge")}
        >
          Edge Automations
        </button>
        <button
          type="button"
          className={`rounded-xl px-4 py-2 text-sm font-medium ${tab === "mesh" ? "bg-cream-alt text-ink-primary" : "text-ink-secondary"}`}
          onClick={() => setTab("mesh")}
        >
          Mesh Workflows
        </button>
      </div>
      {tab === "edge" ? <AutomationStudioCanvas /> : <MeshWorkflowCanvas />}
    </HqPageContent>
  );
}
