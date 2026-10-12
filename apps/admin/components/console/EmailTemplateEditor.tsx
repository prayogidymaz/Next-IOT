"use client";

import { useEffect, useState } from "react";

import { AdminCard } from "@/components/ui/AdminCard";
import { fetchEmailTemplates, previewEmailTemplate, updateEmailTemplate } from "@/lib/api/step9c-admin";

export function EmailTemplateEditor({ code }: { code: string }) {
  const [subject, setSubject] = useState("");
  const [bodyHtml, setBodyHtml] = useState("");
  const [variables, setVariables] = useState<{ name: string; description: string }[]>([]);
  const [preview, setPreview] = useState<{ subject: string; body_html: string } | null>(null);
  const [sample, setSample] = useState<Record<string, string>>({});

  useEffect(() => {
    void fetchEmailTemplates().then((rows) => {
      const row = rows.find((r) => r.code === code);
      if (!row) return;
      setSubject(row.subject);
      setBodyHtml(row.body_html);
      setVariables(row.variables);
      const init: Record<string, string> = {};
      for (const v of row.variables) init[v.name] = "";
      setSample(init);
    });
  }, [code]);

  return (
    <div className="grid gap-4 lg:grid-cols-2">
      <AdminCard className="space-y-3 p-4">
        <div className="flex flex-wrap gap-2">
          {variables.map((v) => (
            <span key={v.name} className="rounded-full bg-slate-100 px-2 py-1 text-xs" title={v.description}>
              {`{{ ${v.name} }}`}
            </span>
          ))}
        </div>
        <label className="block text-sm">
          Subject
          <input className="admin-input mt-1 w-full" value={subject} onChange={(e) => setSubject(e.target.value)} />
        </label>
        <label className="block text-sm">
          HTML body
          <textarea className="admin-input mt-1 w-full font-mono text-xs" rows={14} value={bodyHtml} onChange={(e) => setBodyHtml(e.target.value)} />
        </label>
        <div className="flex flex-wrap gap-2">
          <button
            type="button"
            className="rounded bg-blue-800 px-3 py-2 text-sm text-white"
            onClick={() => void updateEmailTemplate(code, { subject, body_html: bodyHtml })}
          >
            Save
          </button>
          <button
            type="button"
            className="rounded border px-3 py-2 text-sm"
            onClick={() => void previewEmailTemplate(code, sample).then(setPreview)}
          >
            Preview
          </button>
        </div>
        {variables.map((v) => (
          <input
            key={v.name}
            className="admin-input w-full text-sm"
            placeholder={`Sample ${v.name}`}
            value={sample[v.name] ?? ""}
            onChange={(e) => setSample((s) => ({ ...s, [v.name]: e.target.value }))}
          />
        ))}
      </AdminCard>
      <AdminCard className="p-4">
        <h3 className="text-sm font-semibold">Live preview</h3>
        {preview ? (
          <>
            <p className="mt-2 text-sm font-medium">{preview.subject}</p>
            <iframe title="preview" className="mt-3 h-96 w-full rounded border bg-white" srcDoc={preview.body_html} />
          </>
        ) : (
          <p className="mt-4 text-sm text-slate-500">Click Preview to render HTML.</p>
        )}
      </AdminCard>
    </div>
  );
}
