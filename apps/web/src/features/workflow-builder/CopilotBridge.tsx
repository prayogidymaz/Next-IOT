"use client";

import { useState } from "react";

import { draftToFlow } from "./serializer";
import type { WorkflowDraft } from "./types";

type Props = {
  apiBase: string;
  token: string;
  onApply: (nodes: ReturnType<typeof draftToFlow>["nodes"], edges: ReturnType<typeof draftToFlow>["edges"]) => void;
};

export function CopilotBridge({ apiBase, token, onApply }: Props) {
  const [open, setOpen] = useState(false);
  const [prompt, setPrompt] = useState("");
  const [preview, setPreview] = useState<WorkflowDraft | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  async function generate() {
    setLoading(true);
    setError(null);
    try {
      const resp = await fetch(`${apiBase}/api/v1/mesh/copilot/generate-workflow`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify({ prompt, locale: "id" }),
      });
      if (!resp.ok) {
        throw new Error(`Copilot error ${resp.status}`);
      }
      const body = (await resp.json()) as { draft: WorkflowDraft };
      setPreview(body.draft);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed");
    } finally {
      setLoading(false);
    }
  }

  function apply() {
    if (!preview) return;
    const { nodes, edges } = draftToFlow(preview);
    onApply(nodes, edges);
    setOpen(false);
    setPreview(null);
    setPrompt("");
  }

  if (!open) {
    return (
      <button
        type="button"
        className="rounded bg-emerald-700 px-3 py-1.5 text-sm text-white"
        onClick={() => setOpen(true)}
      >
        Generate from AI
      </button>
    );
  }

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/40 p-4">
      <div className="w-full max-w-lg rounded-lg bg-white p-4 shadow-xl">
        <h2 className="text-lg font-semibold">Copilot — Bahasa Indonesia</h2>
        <textarea
          className="mt-3 h-28 w-full rounded border p-2 text-sm"
          placeholder="Contoh: kalau tanah plot A kering siram 15 menit"
          value={prompt}
          onChange={(e) => setPrompt(e.target.value)}
        />
        {error ? <p className="mt-2 text-sm text-red-600">{error}</p> : null}
        {preview ? (
          <pre className="mt-2 max-h-40 overflow-auto rounded bg-stone-50 p-2 text-xs">
            {JSON.stringify(preview, null, 2)}
          </pre>
        ) : null}
        <div className="mt-4 flex justify-end gap-2">
          <button type="button" className="rounded border px-3 py-1.5 text-sm" onClick={() => setOpen(false)}>
            Cancel
          </button>
          <button
            type="button"
            disabled={loading || prompt.length < 3}
            className="rounded bg-stone-800 px-3 py-1.5 text-sm text-white disabled:opacity-50"
            onClick={() => void generate()}
          >
            {loading ? "Generating…" : "Preview"}
          </button>
          <button
            type="button"
            disabled={!preview}
            className="rounded bg-emerald-700 px-3 py-1.5 text-sm text-white disabled:opacity-50"
            onClick={apply}
          >
            Apply to canvas
          </button>
        </div>
      </div>
    </div>
  );
}
