"use client";

import { useState } from "react";

import { requestWorkflowApproval } from "@/lib/api/workflowApproval";
import { useHqToast } from "@/hooks/useHqToast";

type Props = {
  workflowId: string;
  open: boolean;
  onClose: () => void;
  onSubmitted?: () => void;
};

export function ApprovalRequestModal({ workflowId, open, onClose, onSubmitted }: Props) {
  const { showToast } = useHqToast();
  const [notes, setNotes] = useState("");
  const [submitting, setSubmitting] = useState(false);

  if (!open) return null;

  async function submit() {
    setSubmitting(true);
    try {
      await requestWorkflowApproval(workflowId, notes);
      showToast("Approval request submitted", "success");
      setNotes("");
      onClose();
      onSubmitted?.();
    } catch (e: unknown) {
      showToast(e instanceof Error ? e.message : "Request failed", "error");
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/40 p-4">
      <div className="w-full max-w-md rounded-xl bg-white p-4 shadow-xl">
        <h2 className="text-lg font-semibold text-stone-900">Request approval</h2>
        <p className="mt-1 text-sm text-stone-600">Required before production activation when policy is enabled.</p>
        <label className="mt-4 block text-xs font-medium text-stone-600">
          Notes
          <textarea
            className="mt-1 w-full rounded-lg border border-stone-300 px-3 py-2 text-sm"
            rows={4}
            value={notes}
            onChange={(e) => setNotes(e.target.value)}
            placeholder="Describe changes for reviewers…"
          />
        </label>
        <div className="mt-4 flex justify-end gap-2">
          <button type="button" className="rounded border px-3 py-1.5 text-sm" onClick={onClose} disabled={submitting}>
            Cancel
          </button>
          <button
            type="button"
            className="rounded bg-stone-900 px-3 py-1.5 text-sm text-white disabled:opacity-50"
            disabled={submitting}
            onClick={() => void submit()}
          >
            Submit
          </button>
        </div>
      </div>
    </div>
  );
}
