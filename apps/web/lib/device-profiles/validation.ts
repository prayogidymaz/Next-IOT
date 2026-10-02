import type { ThingModelSpec } from "@/lib/api/device-profiles-schemas";

const KEY_REGEX = /^[a-z0-9_]{1,64}$/;

export type ClientValidationIssue = {
  path: string;
  message: string;
};

export function validateProfileKey(key: string): string | null {
  if (!KEY_REGEX.test(key)) {
    return "Key hanya [a-z0-9_], maks 64 karakter.";
  }
  return null;
}

export function validateThingModelSpec(spec: ThingModelSpec): ClientValidationIssue[] {
  const issues: ClientValidationIssue[] = [];
  if (spec.telemetry.length > 200) {
    issues.push({ path: "telemetry", message: "Maksimal 200 telemetry key." });
  }

  const allKeys = new Set<string>();
  for (const entry of spec.telemetry) {
    const keyErr = validateProfileKey(entry.key);
    if (keyErr) issues.push({ path: `telemetry.${entry.key}`, message: keyErr });
    if (allKeys.has(entry.key)) issues.push({ path: `telemetry.${entry.key}`, message: "Key duplikat." });
    allKeys.add(entry.key);
    if (entry.data_type === "number" || entry.data_type === "integer") {
      if (entry.min !== undefined && entry.min !== null && entry.max !== undefined && entry.max !== null) {
        if (entry.min > entry.max) {
          issues.push({ path: `telemetry.${entry.key}`, message: "min tidak boleh lebih besar dari max." });
        }
      }
    }
    if (entry.data_type === "enum" && entry.values.length < 1) {
      issues.push({ path: `telemetry.${entry.key}`, message: "Enum butuh minimal 1 nilai." });
    }
  }

  for (const entry of spec.attributes) {
    const keyErr = validateProfileKey(entry.key);
    if (keyErr) issues.push({ path: `attributes.${entry.key}`, message: keyErr });
    if (allKeys.has(entry.key)) issues.push({ path: `attributes.${entry.key}`, message: "Key duplikat." });
    allKeys.add(entry.key);
    if (entry.data_type === "enum" && entry.values.length < 1) {
      issues.push({ path: `attributes.${entry.key}`, message: "Enum butuh minimal 1 nilai." });
    }
  }

  for (const cmd of spec.commands) {
    const keyErr = validateProfileKey(cmd.key);
    if (keyErr) issues.push({ path: `commands.${cmd.key}`, message: keyErr });
    if (allKeys.has(cmd.key)) issues.push({ path: `commands.${cmd.key}`, message: "Key duplikat." });
    allKeys.add(cmd.key);
    if (cmd.timeout_seconds < 1 || cmd.timeout_seconds > 300) {
      issues.push({ path: `commands.${cmd.key}`, message: "timeout_seconds harus 1–300." });
    }
    const paramKeys = new Set<string>();
    for (const param of cmd.params) {
      const pErr = validateProfileKey(param.key);
      if (pErr) issues.push({ path: `commands.${cmd.key}.${param.key}`, message: pErr });
      if (paramKeys.has(param.key)) {
        issues.push({ path: `commands.${cmd.key}.${param.key}`, message: "Parameter duplikat." });
      }
      paramKeys.add(param.key);
      if (param.data_type === "enum" && param.values.length < 1) {
        issues.push({ path: `commands.${cmd.key}.${param.key}`, message: "Enum butuh minimal 1 nilai." });
      }
    }
  }

  return issues;
}
