/**
 * Sync microbiome-refs.yaml → workspace/registry/references.yaml
 *
 * Usage:
 *   npm run build && npm run sync-refs
 *   node scripts/sync-refs.mjs [--refs PATH] [--workspace PATH] [--mode auto|docker|host]
 */
import fs from "node:fs";
import path from "node:path";
import { fileURLToPath, pathToFileURL } from "node:url";

const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "..");

function argValue(flag) {
  const i = process.argv.indexOf(flag);
  if (i >= 0 && process.argv[i + 1]) return process.argv[i + 1];
  return undefined;
}

async function main() {
  const distSync = path.join(root, "dist/refs/sync.js");
  if (!fs.existsSync(distSync)) {
    throw new Error("dist/refs/sync.js missing — run `npm run build` first");
  }

  const { syncReferences, defaultRefsConfigPath } = await import(
    pathToFileURL(distSync).href
  );

  const refsConfigPath =
    argValue("--refs") ||
    process.env.MGX_REFS_CONFIG ||
    defaultRefsConfigPath();
  const workspaceRoot =
    argValue("--workspace") ||
    process.env.OPENCLAW_WORKSPACE ||
    process.env.OPENCLAW_WORKSPACE_DIR ||
    path.join(root, "workspace");
  const mode = argValue("--mode") || process.env.MGX_REFS_MODE || "auto";

  const result = syncReferences({
    refsConfigPath,
    workspaceRoot,
    mode,
  });

  console.log("");
  console.log(`refsConfig:  ${result.refsConfigPath}`);
  console.log(`workspace:   ${workspaceRoot}`);
  console.log(`output:      ${result.outputPath}`);
  console.log(`mode:        ${result.mode}`);
  console.log(`refs:        ${Object.keys(result.generated.references).length}`);
  if (result.missingConfig) {
    console.log(`(missing config — copied empty placeholder)`);
  }
  if (result.recommendedExtraMounts.length > 0) {
    console.log("");
    console.log("Docker (gateway container):");
    console.log(
      `  export OPENCLAW_EXTRA_MOUNTS=${result.recommendedExtraMounts.join(",")}`,
    );
    console.log("  # then re-run scripts/docker/setup.sh or compose with extra.yml");
  }
}

main().catch((err) => {
  console.error(err);
  process.exit(1);
});
