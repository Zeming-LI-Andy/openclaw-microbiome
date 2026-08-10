import fs from "node:fs";
import {
  defaultRefsConfigPath,
  emptyGeneratedReferences,
  expandHome,
  loadUserRefsConfig,
  resolveReferences,
} from "./resolve.js";
import type { ResolveRefsResult, SyncReferencesOptions } from "./types.js";
import { writeGeneratedReferences } from "./write.js";

export type SyncReferencesResult = ResolveRefsResult & {
  refsConfigPath: string;
  outputPath: string;
  missingConfig: boolean;
};

/**
 * Load user microbiome-refs.yaml (if present), resolve paths, write
 * workspace/registry/references.yaml.
 */
export function syncReferences(options: SyncReferencesOptions): SyncReferencesResult {
  const log = options.log ?? console;
  const refsConfigPath = expandHome(options.refsConfigPath || defaultRefsConfigPath());
  const workspaceRoot = expandHome(options.workspaceRoot);

  if (!fs.existsSync(refsConfigPath)) {
    log.warn(
      `[microbiome] refs config not found: ${refsConfigPath} — writing empty references.yaml`,
    );
    const generated = emptyGeneratedReferences();
    const outputPath = writeGeneratedReferences(workspaceRoot, generated);
    return {
      mode: "host",
      generated,
      recommendedExtraMounts: [],
      warnings: [`missing refs config: ${refsConfigPath}`],
      refsConfigPath,
      outputPath,
      missingConfig: true,
    };
  }

  const cfg = loadUserRefsConfig(refsConfigPath);
  const resolved = resolveReferences(cfg, {
    mode: options.mode,
    isDockerEnv: options.isDockerEnv,
  });

  for (const w of resolved.warnings) {
    log.warn(`[microbiome] refs: ${w}`);
  }

  const outputPath = writeGeneratedReferences(workspaceRoot, resolved.generated);
  log.info(
    `[microbiome] wrote ${outputPath} (${Object.keys(resolved.generated.references).length} refs, mode=${resolved.mode})`,
  );

  if (resolved.recommendedExtraMounts.length > 0) {
    log.info(
      `[microbiome] Docker: set OPENCLAW_EXTRA_MOUNTS=${resolved.recommendedExtraMounts.join(",")}`,
    );
  }

  return {
    ...resolved,
    refsConfigPath,
    outputPath,
    missingConfig: false,
  };
}

export { defaultRefsConfigPath, expandHome };
