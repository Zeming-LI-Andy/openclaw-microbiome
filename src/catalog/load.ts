import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";
import { parse as parseYaml } from "yaml";
import type { Catalog, PluginConfig, ToolSpec } from "../runtime/types.js";

const HERE = path.dirname(fileURLToPath(import.meta.url));

export function defaultCatalogDir(): string {
  const candidates = [
    path.resolve(HERE, "../../catalog"),
    path.resolve(HERE, "../catalog"),
    path.resolve(process.cwd(), "catalog"),
  ];
  for (const c of candidates) {
    if (fs.existsSync(path.join(c, "tools.yaml"))) return c;
  }
  return candidates[0]!;
}

/** Load plugin tool definitions (tools.yaml only). Host runtimes live in workspace/registry/. */
export function loadCatalog(config: PluginConfig = {}): Catalog {
  const dir = config.catalogDir ? path.resolve(config.catalogDir) : defaultCatalogDir();
  const toolsPath = path.join(dir, "tools.yaml");
  if (!fs.existsSync(toolsPath)) {
    throw new Error(`Catalog not found under ${dir} (expected tools.yaml)`);
  }

  const toolsDoc = parseYaml(fs.readFileSync(toolsPath, "utf8")) as {
    tools?: ToolSpec[];
  };

  const tools = (toolsDoc.tools ?? []).map((t) => ({
    ...t,
    optional: Boolean(t.optional),
  }));

  return { runtimes: {}, tools };
}

export function listToolIds(catalog: Catalog): string[] {
  return catalog.tools.map((t) => t.id);
}
