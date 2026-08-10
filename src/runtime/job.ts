import fs from "node:fs";
import path from "node:path";
import { randomBytes } from "node:crypto";
import type { JobPaths, PluginConfig } from "./types.js";

export type SessionJobResult = JobPaths & {
  reused: boolean;
  source: "env" | "bookmark" | "created";
  bookmark_path: string;
  jobs_root: string;
};

export function resolveJobsRoot(config: PluginConfig): string {
  if (config.jobsRoot) return path.resolve(config.jobsRoot);
  if (process.env.OPENCLAW_JOBS_ROOT) {
    return path.resolve(process.env.OPENCLAW_JOBS_ROOT);
  }
  return path.resolve(process.cwd(), "jobs");
}

/** Workspace checkout that holds the session bookmark `.current_job_id`. */
export function resolveWorkspaceRoot(config: PluginConfig): string {
  if (config.workspaceRoot) return path.resolve(config.workspaceRoot);
  if (process.env.OPENCLAW_WORKSPACE) {
    return path.resolve(process.env.OPENCLAW_WORKSPACE);
  }
  return path.resolve(process.cwd());
}

function bookmarkPath(config: PluginConfig): string {
  return path.join(resolveWorkspaceRoot(config), ".current_job_id");
}

function mintJobId(label?: string): string {
  // MetaClaw-style: YYYYMMDD-HHMMSS-<8 hex>
  const now = new Date();
  const pad = (n: number, w = 2) => String(n).padStart(w, "0");
  const stamp = [
    now.getFullYear(),
    pad(now.getMonth() + 1),
    pad(now.getDate()),
    "-",
    pad(now.getHours()),
    pad(now.getMinutes()),
    pad(now.getSeconds()),
  ].join("");
  const suffix = randomBytes(4).toString("hex");
  if (!label) return `${stamp}-${suffix}`;
  const slug = label
    .toLowerCase()
    .replace(/[^a-z0-9]+/g, "-")
    .replace(/^-+|-+$/g, "")
    .slice(0, 40);
  return slug ? `${stamp}-${slug}-${suffix}` : `${stamp}-${suffix}`;
}

export function jobPaths(root: string, jobId?: string): JobPaths {
  const id = jobId ?? path.basename(root);
  return {
    jobId: id,
    root,
    stage: path.join(root, "stage"),
    analysis: path.join(root, "analysis"),
    reproducibility: path.join(root, "reproducibility"),
    logs: path.join(root, "reproducibility", "logs"),
  };
}

function ensureJobTree(paths: JobPaths): void {
  for (const dir of [
    paths.root,
    paths.stage,
    paths.analysis,
    paths.reproducibility,
    paths.logs,
    path.join(paths.reproducibility, "generated_scripts"),
  ]) {
    fs.mkdirSync(dir, { recursive: true });
  }
}

function tryReuse(config: PluginConfig, jobId: string, source: "env" | "bookmark"): SessionJobResult | null {
  if (!jobId || jobId.includes("..") || path.isAbsolute(jobId) || jobId.includes("/") || jobId.includes("\\")) {
    return null;
  }
  const jobsRoot = resolveJobsRoot(config);
  const root = path.join(jobsRoot, jobId);
  if (!fs.existsSync(root)) return null;
  const paths = jobPaths(root, jobId);
  ensureJobTree(paths);
  return {
    ...paths,
    reused: true,
    source,
    bookmark_path: bookmarkPath(config),
    jobs_root: jobsRoot,
  };
}

/**
 * One OpenClaw session ↔ one job_id (MetaClaw gateway convention).
 * Resolve order: OPENCLAW_SESSION_JOB_ID → workspace `.current_job_id` → create.
 */
export function createOrReuseSessionJob(
  config: PluginConfig,
  opts: { label?: string; notes?: string; forceNew?: boolean } = {},
): SessionJobResult {
  const jobsRoot = resolveJobsRoot(config);
  const bookmark = bookmarkPath(config);
  fs.mkdirSync(jobsRoot, { recursive: true });
  fs.mkdirSync(path.dirname(bookmark), { recursive: true });

  if (!opts.forceNew) {
    const fromEnv = process.env.OPENCLAW_SESSION_JOB_ID?.trim();
    if (fromEnv) {
      const reused = tryReuse(config, fromEnv, "env");
      if (reused) return reused;
    }
    if (fs.existsSync(bookmark)) {
      const fromFile = fs.readFileSync(bookmark, "utf8").trim();
      const reused = tryReuse(config, fromFile, "bookmark");
      if (reused) return reused;
    }
  }

  const jobId = mintJobId(opts.label);
  const root = path.join(jobsRoot, jobId);
  const paths = jobPaths(root, jobId);
  ensureJobTree(paths);

  const meta = {
    job_id: jobId,
    label: opts.label ?? null,
    notes: opts.notes ?? null,
    created_at: new Date().toISOString(),
  };
  fs.writeFileSync(path.join(paths.root, "job.json"), JSON.stringify(meta, null, 2));
  fs.writeFileSync(bookmark, `${jobId}\n`);

  return {
    ...paths,
    reused: false,
    source: "created",
    bookmark_path: bookmark,
    jobs_root: jobsRoot,
  };
}

/** @deprecated use createOrReuseSessionJob */
export function createJob(config: PluginConfig, label?: string, notes?: string): JobPaths {
  return createOrReuseSessionJob(config, { label, notes, forceNew: true });
}

export function resolveJob(config: PluginConfig, jobId: string): JobPaths {
  if (!jobId || jobId.includes("..") || path.isAbsolute(jobId)) {
    throw new Error(`Invalid job_id: ${jobId}`);
  }
  const root = path.join(resolveJobsRoot(config), jobId);
  if (!fs.existsSync(root)) {
    throw new Error(`Job not found: ${jobId} (looked in ${root})`);
  }
  return jobPaths(root, jobId);
}
