import { z } from "zod";

export const profileDomainSchema = z.enum([
  "smart_home",
  "smart_farming",
  "cyberdeck",
  "drone",
  "robotics",
  "industrial",
  "generic",
]);

export const profileStatusSchema = z.enum(["draft", "published", "archived"]);

export const dataTypeSchema = z.enum(["number", "integer", "boolean", "string", "enum"]);

export const attributeScopeSchema = z.enum(["server", "shared", "client"]);

const keyField = z.string().min(1).max(64);

const telemetryKeyNumberSchema = z.object({
  key: keyField,
  label: z.string(),
  unit: z.string().nullable().optional(),
  data_type: z.literal("number"),
  min: z.number().nullable().optional(),
  max: z.number().nullable().optional(),
  precision: z.number().int().min(0).max(10).nullable().optional(),
});

const telemetryKeyIntegerSchema = z.object({
  key: keyField,
  label: z.string(),
  unit: z.string().nullable().optional(),
  data_type: z.literal("integer"),
  min: z.number().int().nullable().optional(),
  max: z.number().int().nullable().optional(),
});

const telemetryKeyBooleanSchema = z.object({
  key: keyField,
  label: z.string(),
  unit: z.string().nullable().optional(),
  data_type: z.literal("boolean"),
});

const telemetryKeyStringSchema = z.object({
  key: keyField,
  label: z.string(),
  unit: z.string().nullable().optional(),
  data_type: z.literal("string"),
});

const telemetryKeyEnumSchema = z.object({
  key: keyField,
  label: z.string(),
  unit: z.string().nullable().optional(),
  data_type: z.literal("enum"),
  values: z.array(z.string()).min(1),
});

export const telemetryKeySchema = z.discriminatedUnion("data_type", [
  telemetryKeyNumberSchema,
  telemetryKeyIntegerSchema,
  telemetryKeyBooleanSchema,
  telemetryKeyStringSchema,
  telemetryKeyEnumSchema,
]);

const attributeDefNumberSchema = z.object({
  key: keyField,
  label: z.string(),
  scope: attributeScopeSchema,
  data_type: z.literal("number"),
  default: z.number().nullable().optional(),
  min: z.number().nullable().optional(),
  max: z.number().nullable().optional(),
  precision: z.number().int().min(0).max(10).nullable().optional(),
});

const attributeDefIntegerSchema = z.object({
  key: keyField,
  label: z.string(),
  scope: attributeScopeSchema,
  data_type: z.literal("integer"),
  default: z.number().int().nullable().optional(),
  min: z.number().int().nullable().optional(),
  max: z.number().int().nullable().optional(),
});

const attributeDefBooleanSchema = z.object({
  key: keyField,
  label: z.string(),
  scope: attributeScopeSchema,
  data_type: z.literal("boolean"),
  default: z.boolean().nullable().optional(),
});

const attributeDefStringSchema = z.object({
  key: keyField,
  label: z.string(),
  scope: attributeScopeSchema,
  data_type: z.literal("string"),
  default: z.string().nullable().optional(),
});

const attributeDefEnumSchema = z.object({
  key: keyField,
  label: z.string(),
  scope: attributeScopeSchema,
  data_type: z.literal("enum"),
  values: z.array(z.string()).min(1),
  default: z.string().nullable().optional(),
});

export const attributeDefSchema = z.discriminatedUnion("data_type", [
  attributeDefNumberSchema,
  attributeDefIntegerSchema,
  attributeDefBooleanSchema,
  attributeDefStringSchema,
  attributeDefEnumSchema,
]);

const commandParamNumberSchema = z.object({
  key: keyField,
  data_type: z.literal("number"),
  required: z.boolean().optional().default(true),
  min: z.number().nullable().optional(),
  max: z.number().nullable().optional(),
  precision: z.number().int().min(0).max(10).nullable().optional(),
});

const commandParamIntegerSchema = z.object({
  key: keyField,
  data_type: z.literal("integer"),
  required: z.boolean().optional().default(true),
  min: z.number().int().nullable().optional(),
  max: z.number().int().nullable().optional(),
});

const commandParamBooleanSchema = z.object({
  key: keyField,
  data_type: z.literal("boolean"),
  required: z.boolean().optional().default(true),
});

const commandParamStringSchema = z.object({
  key: keyField,
  data_type: z.literal("string"),
  required: z.boolean().optional().default(true),
});

const commandParamEnumSchema = z.object({
  key: keyField,
  data_type: z.literal("enum"),
  required: z.boolean().optional().default(true),
  values: z.array(z.string()).min(1),
});

export const commandParamSchema = z.discriminatedUnion("data_type", [
  commandParamNumberSchema,
  commandParamIntegerSchema,
  commandParamBooleanSchema,
  commandParamStringSchema,
  commandParamEnumSchema,
]);

export const commandDefSchema = z.object({
  key: keyField,
  label: z.string(),
  params: z.array(commandParamSchema),
  timeout_seconds: z.number().int().min(1).max(300),
});

export const thingModelSpecSchema = z.object({
  telemetry: z.array(telemetryKeySchema).max(200),
  attributes: z.array(attributeDefSchema),
  commands: z.array(commandDefSchema),
});

export const deviceProfileSchema = z.object({
  id: z.string().uuid(),
  tenant_id: z.string().uuid(),
  key: z.string(),
  name: z.string(),
  description: z.string(),
  domain: profileDomainSchema,
  version: z.number().int(),
  status: profileStatusSchema,
  spec: thingModelSpecSchema,
  created_at: z.string(),
  updated_at: z.string(),
});

export type ProfileDomain = z.infer<typeof profileDomainSchema>;
export type ProfileStatus = z.infer<typeof profileStatusSchema>;
export type DataType = z.infer<typeof dataTypeSchema>;
export type TelemetryKey = z.infer<typeof telemetryKeySchema>;
export type AttributeDef = z.infer<typeof attributeDefSchema>;
export type CommandParam = z.infer<typeof commandParamSchema>;
export type CommandDef = z.infer<typeof commandDefSchema>;
export type ThingModelSpec = z.infer<typeof thingModelSpecSchema>;
export type DeviceProfile = z.infer<typeof deviceProfileSchema>;
