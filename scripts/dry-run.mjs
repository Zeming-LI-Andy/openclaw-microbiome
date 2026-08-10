/**
 * Dry-run: create session job, second call reuses bookmark.
 */
import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";
import { pathToFileURL } from "node:url";

const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "..");

async function main() {
  const { loadCatalog } = await import(pathToFileURL(path.join(root, "dist/catalog/load.js")).href);
  const { buildTools } = await import(pathToFileURL(path.join(root, "dist/tools/register.js")).href);

  const work = path.join(root, ".dry-run-workspace");
  fs.mkdirSync(work, { recursive: true });
  const bookmark = path.join(work, ".current_job_id");
  if (fs.existsSync(bookmark)) fs.unlinkSync(bookmark);

  const config = {
    jobsRoot: path.join(root, "jobs"),
    workspaceRoot: work,
    catalogDir: path.join(root, "catalog"),
  };

  const catalog = loadCatalog(config);
  const tools = Object.fromEntries(buildTools(catalog, () => config).map((t) => [t.name, t]));

  const created = await tools.mgx_create_job.execute({ label: "dry-run-16s" });
  console.log("created:", JSON.stringify(created.details, null, 2));

  const reused = await tools.mgx_create_job.execute({});
  console.log("reused:", JSON.stringify(reused.details, null, 2));

  if (!reused.details.reused || reused.details.job_id !== created.details.job_id) {
    throw new Error("expected session job reuse");
  }
  console.log("\nDry-run OK");
}

main().catch((err) => {
  console.error(err);
  process.exit(1);
});
