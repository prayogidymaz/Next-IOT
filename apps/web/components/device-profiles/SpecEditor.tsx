"use client";

import { Plus, Trash2 } from "lucide-react";
import { useState } from "react";

import type {
  AttributeDef,
  CommandDef,
  CommandParam,
  DataType,
  TelemetryKey,
  ThingModelSpec,
} from "@/lib/api/device-profiles-schemas";
import { CreamCard } from "@/components/ui/CreamCard";

type TabId = "telemetry" | "attributes" | "commands";

type SpecEditorProps = {
  spec: ThingModelSpec;
  onChange: (next: ThingModelSpec) => void;
  readOnly: boolean;
};

function newTelemetry(dataType: DataType): TelemetryKey {
  if (dataType === "number") {
    return { key: "metric", label: "Metric", data_type: "number" };
  }
  if (dataType === "integer") {
    return { key: "count", label: "Count", data_type: "integer" };
  }
  if (dataType === "boolean") {
    return { key: "flag", label: "Flag", data_type: "boolean" };
  }
  if (dataType === "string") {
    return { key: "text", label: "Text", data_type: "string" };
  }
  return { key: "mode", label: "Mode", data_type: "enum", values: ["on", "off"] };
}

function newAttribute(dataType: DataType): AttributeDef {
  if (dataType === "number") {
    return { key: "attr", label: "Attribute", scope: "shared", data_type: "number" };
  }
  if (dataType === "integer") {
    return { key: "attr", label: "Attribute", scope: "shared", data_type: "integer" };
  }
  if (dataType === "boolean") {
    return { key: "attr", label: "Attribute", scope: "shared", data_type: "boolean" };
  }
  if (dataType === "string") {
    return { key: "attr", label: "Attribute", scope: "shared", data_type: "string" };
  }
  return { key: "attr", label: "Attribute", scope: "shared", data_type: "enum", values: ["a"] };
}

function newCommand(): CommandDef {
  return { key: "action", label: "Action", params: [], timeout_seconds: 30 };
}

function newCommandParam(dataType: DataType): CommandParam {
  if (dataType === "number") return { key: "value", data_type: "number", required: true };
  if (dataType === "integer") return { key: "value", data_type: "integer", required: true };
  if (dataType === "boolean") return { key: "flag", data_type: "boolean", required: true };
  if (dataType === "string") return { key: "text", data_type: "string", required: true };
  return { key: "mode", data_type: "enum", required: true, values: ["a"] };
}

const inputClass =
  "mt-1 w-full rounded-xl border border-cream-border bg-white px-3 py-2 text-sm text-ink-primary outline-none ring-accent-cobalt/30 focus:ring-2 disabled:bg-cream-muted";

export function SpecEditor({ spec, onChange, readOnly }: SpecEditorProps) {
  const [tab, setTab] = useState<TabId>("telemetry");

  return (
    <CreamCard className="p-5">
      <div className="mb-4 flex flex-wrap gap-2">
        {(["telemetry", "attributes", "commands"] as TabId[]).map((id) => (
          <button
            key={id}
            type="button"
            onClick={() => setTab(id)}
            className={`rounded-full px-3 py-1.5 text-xs font-semibold capitalize ${
              tab === id ? "bg-ink-primary text-white" : "bg-cream-muted text-ink-secondary"
            }`}
          >
            {id}
          </button>
        ))}
      </div>

      {tab === "telemetry" ? (
        <TelemetryTab
          items={spec.telemetry}
          readOnly={readOnly}
          onChange={(telemetry) => onChange({ ...spec, telemetry })}
        />
      ) : null}
      {tab === "attributes" ? (
        <AttributesTab
          items={spec.attributes}
          readOnly={readOnly}
          onChange={(attributes) => onChange({ ...spec, attributes })}
        />
      ) : null}
      {tab === "commands" ? (
        <CommandsTab
          items={spec.commands}
          readOnly={readOnly}
          onChange={(commands) => onChange({ ...spec, commands })}
        />
      ) : null}
    </CreamCard>
  );
}

function TelemetryTab({
  items,
  onChange,
  readOnly,
}: {
  items: TelemetryKey[];
  onChange: (items: TelemetryKey[]) => void;
  readOnly: boolean;
}) {
  return (
    <div className="space-y-4">
      {items.map((item, index) => (
        <div key={`${item.key}-${index}`} className="rounded-xl border border-cream-border bg-cream-alt p-4">
          <div className="grid gap-3 sm:grid-cols-2">
            <label className="text-xs text-ink-secondary">
              Key
              <input
                disabled={readOnly}
                value={item.key}
                onChange={(e) => {
                  const next = [...items];
                  next[index] = { ...item, key: e.target.value };
                  onChange(next);
                }}
                className={inputClass}
              />
            </label>
            <label className="text-xs text-ink-secondary">
              Label
              <input
                disabled={readOnly}
                value={item.label}
                onChange={(e) => {
                  const next = [...items];
                  next[index] = { ...item, label: e.target.value };
                  onChange(next);
                }}
                className={inputClass}
              />
            </label>
            <label className="text-xs text-ink-secondary">
              data_type
              <select
                disabled={readOnly}
                value={item.data_type}
                onChange={(e) => {
                  const dt = e.target.value as DataType;
                  const next = [...items];
                  next[index] = newTelemetry(dt);
                  next[index] = { ...next[index], key: item.key, label: item.label };
                  onChange(next);
                }}
                className={inputClass}
              >
                {["number", "integer", "boolean", "string", "enum"].map((t) => (
                  <option key={t} value={t}>
                    {t}
                  </option>
                ))}
              </select>
            </label>
            {"values" in item ? (
              <label className="text-xs text-ink-secondary sm:col-span-2">
                Enum values (comma-separated)
                <input
                  disabled={readOnly}
                  value={item.values.join(",")}
                  onChange={(e) => {
                    const next = [...items];
                    const current = next[index];
                    if (!current || current.data_type !== "enum") return;
                    next[index] = {
                      ...current,
                      values: e.target.value.split(",").map((v) => v.trim()).filter(Boolean),
                    };
                    onChange(next);
                  }}
                  className={inputClass}
                />
              </label>
            ) : null}
          </div>
          {!readOnly ? (
            <button
              type="button"
              className="mt-3 inline-flex items-center gap-1 text-xs text-red-600"
              onClick={() => onChange(items.filter((_, i) => i !== index))}
            >
              <Trash2 className="h-3 w-3" /> Hapus
            </button>
          ) : null}
        </div>
      ))}
      {!readOnly ? (
        <button
          type="button"
          className="inline-flex items-center gap-2 rounded-xl border border-cream-border bg-white px-3 py-2 text-sm font-medium text-ink-primary"
          onClick={() => onChange([...items, newTelemetry("number")])}
        >
          <Plus className="h-4 w-4" /> Add telemetry
        </button>
      ) : null}
    </div>
  );
}

function AttributesTab({
  items,
  onChange,
  readOnly,
}: {
  items: AttributeDef[];
  onChange: (items: AttributeDef[]) => void;
  readOnly: boolean;
}) {
  return (
    <div className="space-y-4">
      {items.map((item, index) => (
        <div key={`${item.key}-${index}`} className="rounded-xl border border-cream-border bg-cream-alt p-4">
          <div className="grid gap-3 sm:grid-cols-2">
            <label className="text-xs text-ink-secondary">
              Key
              <input
                disabled={readOnly}
                value={item.key}
                onChange={(e) => {
                  const next = [...items];
                  next[index] = { ...item, key: e.target.value };
                  onChange(next);
                }}
                className={inputClass}
              />
            </label>
            <label className="text-xs text-ink-secondary">
              Scope
              <select
                disabled={readOnly}
                value={item.scope}
                onChange={(e) => {
                  const next = [...items];
                  next[index] = { ...item, scope: e.target.value as AttributeDef["scope"] };
                  onChange(next);
                }}
                className={inputClass}
              >
                <option value="server">server</option>
                <option value="shared">shared</option>
                <option value="client">client</option>
              </select>
            </label>
            <label className="text-xs text-ink-secondary">
              data_type
              <select
                disabled={readOnly}
                value={item.data_type}
                onChange={(e) => {
                  const dt = e.target.value as DataType;
                  const next = [...items];
                  next[index] = newAttribute(dt);
                  next[index] = { ...next[index], key: item.key, label: item.label };
                  onChange(next);
                }}
                className={inputClass}
              >
                {["number", "integer", "boolean", "string", "enum"].map((t) => (
                  <option key={t} value={t}>
                    {t}
                  </option>
                ))}
              </select>
            </label>
          </div>
          {!readOnly ? (
            <button
              type="button"
              className="mt-3 inline-flex items-center gap-1 text-xs text-red-600"
              onClick={() => onChange(items.filter((_, i) => i !== index))}
            >
              <Trash2 className="h-3 w-3" /> Hapus
            </button>
          ) : null}
        </div>
      ))}
      {!readOnly ? (
        <button
          type="button"
          className="inline-flex items-center gap-2 rounded-xl border border-cream-border bg-white px-3 py-2 text-sm font-medium"
          onClick={() => onChange([...items, newAttribute("string")])}
        >
          <Plus className="h-4 w-4" /> Add attribute
        </button>
      ) : null}
    </div>
  );
}

function CommandsTab({
  items,
  onChange,
  readOnly,
}: {
  items: CommandDef[];
  onChange: (items: CommandDef[]) => void;
  readOnly: boolean;
}) {
  return (
    <div className="space-y-4">
      {items.map((cmd, cmdIndex) => (
        <div key={`${cmd.key}-${cmdIndex}`} className="rounded-xl border border-cream-border bg-cream-alt p-4">
          <div className="grid gap-3 sm:grid-cols-2">
            <label className="text-xs text-ink-secondary">
              Key
              <input
                disabled={readOnly}
                value={cmd.key}
                onChange={(e) => {
                  const next = [...items];
                  next[cmdIndex] = { ...cmd, key: e.target.value };
                  onChange(next);
                }}
                className={inputClass}
              />
            </label>
            <label className="text-xs text-ink-secondary">
              Timeout (s)
              <input
                type="number"
                min={1}
                max={300}
                disabled={readOnly}
                value={cmd.timeout_seconds}
                onChange={(e) => {
                  const next = [...items];
                  next[cmdIndex] = { ...cmd, timeout_seconds: Number(e.target.value) };
                  onChange(next);
                }}
                className={inputClass}
              />
            </label>
          </div>
          <p className="mt-3 text-xs font-semibold text-ink-secondary">Parameters</p>
          {cmd.params.map((param, paramIndex) => (
            <div key={`${param.key}-${paramIndex}`} className="mt-2 grid gap-2 sm:grid-cols-3">
              <input
                disabled={readOnly}
                value={param.key}
                onChange={(e) => {
                  const next = [...items];
                  const params = [...cmd.params];
                  params[paramIndex] = { ...param, key: e.target.value };
                  next[cmdIndex] = { ...cmd, params };
                  onChange(next);
                }}
                className={inputClass}
                placeholder="param key"
              />
              <select
                disabled={readOnly}
                value={param.data_type}
                onChange={(e) => {
                  const dt = e.target.value as DataType;
                  const next = [...items];
                  const params = [...cmd.params];
                  params[paramIndex] = newCommandParam(dt);
                  params[paramIndex] = { ...params[paramIndex], key: param.key };
                  next[cmdIndex] = { ...cmd, params };
                  onChange(next);
                }}
                className={inputClass}
              >
                {["number", "integer", "boolean", "string", "enum"].map((t) => (
                  <option key={t} value={t}>
                    {t}
                  </option>
                ))}
              </select>
              {!readOnly ? (
                <button
                  type="button"
                  className="text-xs text-red-600"
                  onClick={() => {
                    const next = [...items];
                    next[cmdIndex] = {
                      ...cmd,
                      params: cmd.params.filter((_, i) => i !== paramIndex),
                    };
                    onChange(next);
                  }}
                >
                  Hapus param
                </button>
              ) : null}
            </div>
          ))}
          {!readOnly ? (
            <div className="mt-3 flex flex-wrap gap-2">
              <button
                type="button"
                className="text-xs text-accent-cobalt"
                onClick={() => {
                  const next = [...items];
                  next[cmdIndex] = {
                    ...cmd,
                    params: [...cmd.params, newCommandParam("string")],
                  };
                  onChange(next);
                }}
              >
                + Param
              </button>
              <button
                type="button"
                className="text-xs text-red-600"
                onClick={() => onChange(items.filter((_, i) => i !== cmdIndex))}
              >
                Hapus command
              </button>
            </div>
          ) : null}
        </div>
      ))}
      {!readOnly ? (
        <button
          type="button"
          className="inline-flex items-center gap-2 rounded-xl border border-cream-border bg-white px-3 py-2 text-sm"
          onClick={() => onChange([...items, newCommand()])}
        >
          <Plus className="h-4 w-4" /> Add command
        </button>
      ) : null}
    </div>
  );
}
