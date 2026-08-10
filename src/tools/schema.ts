import { Type, type TSchema } from "typebox";
import type { JsonSchema } from "../runtime/types.js";

/** Minimal JSON Schema → TypeBox conversion for catalog tool parameters. */
export function jsonSchemaToTypeBox(schema: JsonSchema | undefined): TSchema {
  if (!schema) return Type.Object({}, { additionalProperties: false });
  return convertNode(schema);
}

function convertNode(schema: JsonSchema): TSchema {
  if (schema.enum && schema.enum.length > 0) {
    const values = schema.enum as [string | number | boolean, ...(string | number | boolean)[]];
    return Type.Union(values.map((v) => Type.Literal(v as never)));
  }

  switch (schema.type) {
    case "string":
      return Type.String(meta(schema));
    case "integer":
      return Type.Integer(meta(schema));
    case "number":
      return Type.Number(meta(schema));
    case "boolean":
      return Type.Boolean(meta(schema));
    case "array":
      return Type.Array(
        schema.items ? convertNode(schema.items) : Type.Any(),
        meta(schema),
      );
    case "object":
    default:
      return buildObject(schema);
  }
}

function buildObject(schema: JsonSchema): TSchema {
  const required = new Set(schema.required ?? []);
  const properties: Record<string, TSchema> = {};
  for (const [key, value] of Object.entries(schema.properties ?? {})) {
    const base = convertNode(value);
    properties[key] = required.has(key) ? base : Type.Optional(base);
  }
  return Type.Object(properties, {
    additionalProperties: schema.additionalProperties ?? false,
    ...meta(schema),
  });
}

function meta(schema: JsonSchema): { description?: string } {
  return schema.description ? { description: schema.description } : {};
}
