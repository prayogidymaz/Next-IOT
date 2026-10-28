"use client";

import { useFormContext } from "react-hook-form";

import type { WorkflowNodeData } from "./types";

type FormValues = {
  selectedNode: WorkflowNodeData | null;
};

export function NodeInspector() {
  const { register, watch } = useFormContext<FormValues>();
  const node = watch("selectedNode");
  if (!node) {
    return <div className="p-4 text-sm text-stone-500">Select a node to edit properties.</div>;
  }
  return (
    <div className="w-72 space-y-3 border-l border-stone-200 p-4 text-sm">
      <h3 className="font-semibold text-stone-800">Inspector</h3>
      <label className="block">
        Label
        <input className="mt-1 w-full rounded border px-2 py-1" {...register("selectedNode.label")} />
      </label>
      {node.kind === "trigger" && (
        <>
          <label className="block">
            Sensor
            <input className="mt-1 w-full rounded border px-2 py-1" {...register("selectedNode.sensor")} />
          </label>
          <label className="block">
            Threshold
            <input
              type="number"
              className="mt-1 w-full rounded border px-2 py-1"
              {...register("selectedNode.threshold", { valueAsNumber: true })}
            />
          </label>
        </>
      )}
      {node.kind === "action" && (
        <label className="block">
          Duration (minutes)
          <input
            type="number"
            className="mt-1 w-full rounded border px-2 py-1"
            {...register("selectedNode.duration_minutes", { valueAsNumber: true })}
          />
        </label>
      )}
    </div>
  );
}
