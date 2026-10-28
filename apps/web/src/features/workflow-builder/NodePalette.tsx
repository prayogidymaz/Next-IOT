"use client";

import type { DragEvent } from "react";

import type { WorkflowNodeData } from "./types";

const GROUPS: { title: string; items: Partial<WorkflowNodeData>[] }[] = [
  {
    title: "Triggers",
    items: [
      { kind: "trigger", label: "Soil moisture", triggerKind: "sensor_threshold", sensor: "soil_moisture" },
      { kind: "trigger", label: "Schedule", triggerKind: "cron", cron: "0 6 * * *" },
      { kind: "trigger", label: "Mesh event", triggerKind: "event" },
    ],
  },
  {
    title: "Conditions",
    items: [
      { kind: "condition", label: "AND", logic: "and" },
      { kind: "condition", label: "OR", logic: "or" },
      { kind: "condition", label: "NOT", logic: "not" },
    ],
  },
  {
    title: "Actions",
    items: [
      { kind: "action", label: "Open valve", action: "open", actuator: "valve_A1" },
      { kind: "action", label: "Notification", action: "notify" },
      { kind: "action", label: "Webhook", action: "webhook" },
    ],
  },
];

export const DND_MIME = "application/next-iot-workflow-node";

type Props = {
  onDragStart: (event: DragEvent, template: Partial<WorkflowNodeData>) => void;
};

export function NodePalette({ onDragStart }: Props) {
  return (
    <aside className="w-56 shrink-0 space-y-4 border-r border-stone-200 p-3 text-sm">
      {GROUPS.map((group) => (
        <div key={group.title}>
          <h3 className="mb-2 font-semibold text-stone-700">{group.title}</h3>
          <ul className="space-y-1">
            {group.items.map((item) => (
              <li key={`${group.title}-${item.label}`}>
                <button
                  type="button"
                  draggable
                  onDragStart={(e) => onDragStart(e, item)}
                  className="w-full cursor-grab rounded border border-stone-200 bg-stone-50 px-2 py-1 text-left hover:bg-stone-100"
                >
                  {item.label}
                </button>
              </li>
            ))}
          </ul>
        </div>
      ))}
    </aside>
  );
}
