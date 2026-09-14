import { Type } from "typebox";
import { definePluginEntry } from "openclaw/plugin-sdk/plugin-entry";
import { loadCatalog } from "./catalog/load.js";
import {
  defaultRefsConfigPath,
  expandHome,
  syncReferences,
} from "./refs/sync.js";
import type { PluginConfig, RefsMode } from "./runtime/types.js";
import { buildTools } from "./tools/register.js";

export const configSchema = Type.Object({
  jobsRoot: Type.Optional(
    Type.String({
      description:
        "Root directory for analysis jobs (default: OPENCLAW_JOBS_ROOT or ./jobs). Same idea as MetaClaw /data/output.",
    }),
  ),
  workspaceRoot: Type.Optional(
    Type.String({
      description:
        "OpenClaw workspace checkout that stores per-session job bookmarks under .microbiome/session_jobs/ and registry/references.yaml (default: OPENCLAW_WORKSPACE or cwd).",
    }),
  ),
  catalogDir: Type.Optional(
    Type.String({ description: "Override catalog directory containing tools.yaml." }),
  ),
  refsConfig: Type.Optional(
    Type.String({
      description:
        "Path to user microbiome-refs.yaml (default: ~/.openclaw/microbiome-refs.yaml).",
    }),
  ),
  refsMode: Type.Optional(
    Type.Unsafe<"auto" | "docker" | "host">({
      type: "string",
      description:
        "How to emit reference paths: host (bare-metal), docker (container paths), or auto-detect.",
    }),
  ),
});

function readConfig(api: { pluginConfig?: unknown }): PluginConfig {
  const raw = (api.pluginConfig ?? {}) as PluginConfig;
  return {
    jobsRoot: raw.jobsRoot,
    workspaceRoot: raw.workspaceRoot,
    catalogDir: raw.catalogDir,
    refsConfig: raw.refsConfig,
    refsMode: raw.refsMode,
  };
}

function resolveWorkspaceRoot(config: PluginConfig, ctxWorkspaceDir?: string): string {
  const fromConfig = config.workspaceRoot?.trim();
  if (fromConfig) return expandHome(fromConfig);
  if (ctxWorkspaceDir?.trim()) return ctxWorkspaceDir.trim();
  const fromEnv = process.env.OPENCLAW_WORKSPACE?.trim() || process.env.OPENCLAW_WORKSPACE_DIR?.trim();
  if (fromEnv) return expandHome(fromEnv);
  return process.cwd();
}

function runRefsSync(
  config: PluginConfig,
  workspaceRoot: string,
  log: Pick<Console, "info" | "warn" | "error">,
): void {
  try {
    syncReferences({
      refsConfigPath: config.refsConfig?.trim() || defaultRefsConfigPath(),
      workspaceRoot,
      mode: (config.refsMode as RefsMode | undefined) ?? "auto",
      log,
    });
  } catch (err) {
    const msg = err instanceof Error ? err.message : String(err);
    log.error(`[microbiome] refs sync failed: ${msg}`);
  }
}

export default definePluginEntry({
  id: "microbiome",
  name: "Microbiome Tools",
  description:
    "Session job bootstrap for 16S/metagenomics (one OpenClaw session ↔ one job_id). Skills + Bash run the analysis.",
  configSchema,
  register(api) {
    const getConfig = () => readConfig(api);
    const catalog = loadCatalog(getConfig());
    const tools = buildTools(catalog, getConfig);
    for (const tool of tools) {
      // Factory so each turn gets the stable OpenClaw sessionKey for per-conversation jobs.
      api.registerTool(
        (ctx) => ({
          name: tool.name,
          description: tool.description,
          parameters: tool.parameters,
          async execute(_id, params) {
            return tool.execute(params as Record<string, unknown>, {
              sessionKey: ctx.sessionKey,
            });
          },
        }),
        { optional: tool.optional, name: tool.name },
      );
    }

    const log = api.logger ?? console;
    api.on?.("gateway_start", async (_event, ctx) => {
      const config = getConfig();
      const workspaceRoot = resolveWorkspaceRoot(config, ctx?.workspaceDir);
      runRefsSync(config, workspaceRoot, log);
    });

    // Best-effort sync at register time (CLI / tests without gateway_start).
    const config = getConfig();
    if (config.workspaceRoot || process.env.OPENCLAW_WORKSPACE || process.env.OPENCLAW_WORKSPACE_DIR) {
      runRefsSync(config, resolveWorkspaceRoot(config), log);
    }
  },
});
