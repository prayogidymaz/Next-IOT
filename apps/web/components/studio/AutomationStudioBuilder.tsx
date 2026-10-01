"use client";

import { HqPageContent } from "@/components/hq/HqPageContent";

import { AutomationStudioCanvas } from "./automation/AutomationStudioCanvas";

export function AutomationStudioBuilder() {
  return (
    <HqPageContent description="React Flow canvas — Trigger → Condition → Action with JSON import/export and property panel.">
      <AutomationStudioCanvas />
    </HqPageContent>
  );
}
