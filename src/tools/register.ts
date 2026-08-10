import type { Catalog, PluginConfig, ToolSpec } from "../runtime/types.js";
import { executeProjectTool, isProjectTool } from "./project.js";
import { jsonSchemaToTypeBox } from "./schema.js";

export type RegisteredTool = {
  name: string;
  description: string;
  optional: boolean;
  parameters: ReturnType<typeof jsonSchemaToTypeBox>;
  execute: (params: Record<string, unknown>) => Promise<{
    content: Array<{ type: "text"; text: string }>;
    details: unknown;
  }>;
};

export function buildTools(catalog: Catalog, getConfig: () => PluginConfig): RegisteredTool[] {
  return catalog.tools.map((tool) => buildTool(tool, catalog, getConfig));
}

function buildTool(
  tool: ToolSpec,
  catalog: Catalog,
  getConfig: () => PluginConfig,
): RegisteredTool {
  return {
    name: tool.id,
    description: tool.description.trim(),
    optional: Boolean(tool.optional),
    parameters: jsonSchemaToTypeBox(tool.parameters),
    async execute(params) {
      const config = getConfig();
      try {
        if (!isProjectTool(tool.id) && tool.kind !== "project") {
          throw new Error(`Unsupported tool: ${tool.id}. Only mgx_create_job is registered.`);
        }
        const details = await executeProjectTool(tool.id, params, config, catalog);
        return {
          content: [{ type: "text", text: JSON.stringify(details, null, 2) }],
          details,
        };
      } catch (err) {
        const message = err instanceof Error ? err.message : String(err);
        const details = { ok: false, error: message, tool: tool.id };
        return {
          content: [{ type: "text", text: JSON.stringify(details, null, 2) }],
          details,
        };
      }
    },
  };
}
