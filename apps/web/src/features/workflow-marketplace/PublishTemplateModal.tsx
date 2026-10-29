"use client";

import { useState } from "react";

import { publishWorkflowTemplate } from "@/lib/api/workflowMarketplace";
import { useHqToast } from "@/hooks/useHqToast";

const CATEGORIES = ["irrigation", "pest", "greenhouse", "livestock", "general"] as const;

type Props = {
  workflowId: string;
  open: boolean;
  onClose: () => void;
  onPublished?: () => void;
};

export function PublishTemplateModal({ workflowId, open, onClose, onPublished }: Props) {
  const { showToast } = useHqToast();
  const [name, setName] = useState("");
  const [description, setDescription] = useState("");
  const [category, setCategory] = useState<(typeof CATEGORIES)[number]>("general");
  const [tagInput, setTagInput] = useState("");
  const [tags, setTags] = useState<string[]>([]);
  const [busy, setBusy] = useState(false);

  if (!open) return null;

  function addTag() {
    const t = tagInput.trim();
    if (!t || tags.includes(t)) return;
    setTags((prev) => [...prev, t]);
    setTagInput("");
  }

  async function submit() {
    if (!name.trim()) {
      showToast("Name is required", "error");
      return;
    }
    setBusy(true);
    try {
      await publishWorkflowTemplate({
        workflow_id: workflowId,
        name: name.trim(),
        description,
        category,
        tags,
        locale: "id",
      });
      showToast("Published to marketplace", "success");
      onClose();
      onPublished?.();
    } catch (e: unknown) {
      showToast(e instanceof Error ? e.message : "Publish failed", "error");
    } finally {
      setBusy(false);
    }
  }

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/40 p-4">
      <div className="w-full max-w-lg rounded-xl bg-white p-4 shadow-xl">
        <h2 className="text-lg font-semibold text-stone-900">Publish to marketplace</h2>
        <div className="mt-4 space-y-3">
          <label className="block text-xs font-medium text-stone-600">
            Name
            <input className="mt-1 w-full rounded border px-3 py-2 text-sm" value={name} onChange={(e) => setName(e.target.value)} />
          </label>
          <label className="block text-xs font-medium text-stone-600">
            Description
            <textarea
              className="mt-1 w-full rounded border px-3 py-2 text-sm"
              rows={3}
              value={description}
              onChange={(e) => setDescription(e.target.value)}
            />
          </label>
          <label className="block text-xs font-medium text-stone-600">
            Category
            <select className="mt-1 w-full rounded border px-3 py-2 text-sm" value={category} onChange={(e) => setCategory(e.target.value as (typeof CATEGORIES)[number])}>
              {CATEGORIES.map((c) => (
                <option key={c} value={c}>
                  {c}
                </option>
              ))}
            </select>
          </label>
          <div>
            <span className="text-xs font-medium text-stone-600">Tags</span>
            <div className="mt-1 flex gap-2">
              <input
                className="flex-1 rounded border px-3 py-2 text-sm"
                value={tagInput}
                onChange={(e) => setTagInput(e.target.value)}
                onKeyDown={(e) => {
                  if (e.key === "Enter") {
                    e.preventDefault();
                    addTag();
                  }
                }}
              />
              <button type="button" className="rounded border px-3 text-sm" onClick={addTag}>
                Add
              </button>
            </div>
            <div className="mt-2 flex flex-wrap gap-1">
              {tags.map((t) => (
                <span key={t} className="rounded-full bg-stone-100 px-2 py-0.5 text-xs">
                  {t}
                </span>
              ))}
            </div>
          </div>
        </div>
        <div className="mt-4 flex justify-end gap-2">
          <button type="button" className="rounded border px-3 py-1.5 text-sm" onClick={onClose}>
            Cancel
          </button>
          <button type="button" disabled={busy} className="rounded bg-stone-900 px-3 py-1.5 text-sm text-white" onClick={() => void submit()}>
            Publish
          </button>
        </div>
      </div>
    </div>
  );
}
