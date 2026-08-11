/**
 * Dry-run: create session job, second call reuses per-session bookmark;
 * a different sessionId mints a different job.
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
  const sessionDir = path.join(work, ".microbiome", "session_jobs");
  if (fs.existsSync(sessionDir)) fs.rmSync(sessionDir, { recursive: true, force: true });

  const config = {
    jobsRoot: path.join(root, "jobs"),
    workspaceRoot: work,
    catalogDir: path.join(root, "catalog"),
  };

  const catalog = loadCatalog(config);
  const tools = Object.fromEntries(buildTools(catalog, () => config).map((t) => [t.name, t]));
  const sessionA = { sessionId: "dry-run-session-a" };
  const sessionB = { sessionId: "dry-run-session-b" };

  const created = await tools.mgx_create_job.execute({ label: "dry-run-16s" }, sessionA);
  console.log("created:", JSON.stringify(created.details, null, 2));

  const reused = await tools.mgx_create_job.execute({}, sessionA);
  console.log("reused:", JSON.stringify(reused.details, null, 2));

  if (!reused.details.reused || reused.details.job_id !== created.details.job_id) {
    throw new Error("expected same-session job reuse");
  }

  const other = await tools.mgx_create_job.execute({ label: "other-session" }, sessionB);
  console.log("other session:", JSON.stringify(other.details, null, 2));
  if (other.details.job_id === created.details.job_id) {
    throw new Error("expected different session to mint a different job_id");
  }

  console.log("\nDry-run OK");
}

main().catch((err) => {
  console.error(err);
  process.exit(1);
});
