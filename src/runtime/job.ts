import fs from "node:fs";
import path from "node:path";
import { randomBytes } from "node:crypto";
import type { JobPaths, PluginConfig } from "./types.js";

export type SessionJobSource = "env" | "session" | "legacy_bookmark" | "created";

export type SessionJobResult = JobPaths & {
  reused: boolean;
  source: SessionJobSource;
  bookmark_path: string;
  jobs_root: string;
  /** OpenClaw conversation id used for binding (sessionId preferred). */
  session_binding?: string;
};

/** Trusted OpenClaw tool context used to isolate jobs per conversation. */
export type SessionBinding = {
  /** Ephemeral conversation UUID; regenerated on /new and /reset. */
  sessionId?: string;
  /** Stable routing key (e.g. agent:main:…). Fallback when sessionId missing. */
  sessionKey?: string;
};

export function resolveJobsRoot(config: PluginConfig): string {
  if (config.jobsRoot) return path.resolve(config.jobsRoot);
  if (process.env.OPENCLAW_JOBS_ROOT) {
    return path.resolve(process.env.OPENCLAW_JOBS_ROOT);
  }
  return path.resolve(process.cwd(), "jobs");
}

/** Workspace checkout that holds per-session job bookmarks. */
export function resolveWorkspaceRoot(config: PluginConfig): string {
  if (config.workspaceRoot) return path.resolve(config.workspaceRoot);
  if (process.env.OPENCLAW_WORKSPACE) {
    return path.resolve(process.env.OPENCLAW_WORKSPACE);
  }
  return path.resolve(process.cwd());
}

/** Prefer sessionId (per conversation); fall back to sessionKey. */
export function resolveSessionBindingId(binding?: SessionBinding): string | undefined {
  const sessionId = binding?.sessionId?.trim();
  if (sessionId) return sessionId;
  const sessionKey = binding?.sessionKey?.trim();
  if (sessionKey) return sessionKey;
  return undefined;
}

/** Safe single-segment filename for a session binding id. */
export function sanitizeSessionBindingId(raw: string): string {
  const cleaned = raw.replace(/[^a-zA-Z0-9._-]+/g, "_").replace(/^_+|_+$/g, "");
  return (cleaned || "unknown").slice(0, 180);
}

function sessionJobsDir(config: PluginConfig): string {
  return path.join(resolveWorkspaceRoot(config), ".microbiome", "session_jobs");
}

/** Per-conversation bookmark: workspace/.microbiome/session_jobs/<session>. */
export function sessionBookmarkPath(config: PluginConfig, bindingId: string): string {
  return path.join(sessionJobsDir(config), sanitizeSessionBindingId(bindingId));
}

/** @deprecated workspace-wide bookmark; only used when no session binding is available. */
export function legacyBookmarkPath(config: PluginConfig): string {
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

function tryReuse(
  config: PluginConfig,
  jobId: string,
  source: SessionJobSource,
  bookmark_path: string,
  session_binding?: string,
): SessionJobResult | null {
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
    bookmark_path,
    jobs_root: jobsRoot,
    session_binding,
  };
}

function writeBookmark(bookmark: string, jobId: string): void {
  fs.mkdirSync(path.dirname(bookmark), { recursive: true });
  fs.writeFileSync(bookmark, `${jobId}\n`);
}

/**
 * One OpenClaw conversation ↔ one job_id.
 * Resolve order:
 *   per-session bookmark (.microbiome/session_jobs/<sessionId|sessionKey>) →
 *   when no session binding: OPENCLAW_SESSION_JOB_ID → legacy .current_job_id →
 *   create.
 *
 * Never apply process-wide OPENCLAW_SESSION_JOB_ID when a session binding is
 * present — the gateway hosts many conversations in one process.
 */
export function createOrReuseSessionJob(
  config: PluginConfig,
  opts: {
    label?: string;
    notes?: string;
    session?: SessionBinding;
  } = {},
): SessionJobResult {
  const jobsRoot = resolveJobsRoot(config);
  fs.mkdirSync(jobsRoot, { recursive: true });

  const bindingId = resolveSessionBindingId(opts.session);
  const bookmark = bindingId
    ? sessionBookmarkPath(config, bindingId)
    : legacyBookmarkPath(config);

  // OPENCLAW_SESSION_JOB_ID is process-wide on a multi-session gateway.
  // Only honor it when we have no per-conversation binding; otherwise every
  // chat would collapse onto the same job_id.
  if (!bindingId) {
    const fromEnv = process.env.OPENCLAW_SESSION_JOB_ID?.trim();
    if (fromEnv) {
      const reused = tryReuse(config, fromEnv, "env", bookmark);
      if (reused) {
        writeBookmark(bookmark, fromEnv);
        return reused;
      }
    }
  }
  if (bindingId && fs.existsSync(bookmark)) {
    const fromFile = fs.readFileSync(bookmark, "utf8").trim();
    const reused = tryReuse(config, fromFile, "session", bookmark, bindingId);
    if (reused) return reused;
  }
  if (!bindingId && fs.existsSync(bookmark)) {
    const fromFile = fs.readFileSync(bookmark, "utf8").trim();
    const reused = tryReuse(config, fromFile, "legacy_bookmark", bookmark);
    if (reused) return reused;
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
    session_binding: bindingId ?? null,
  };
  fs.writeFileSync(path.join(paths.root, "job.json"), JSON.stringify(meta, null, 2));
  writeBookmark(bookmark, jobId);

  return {
    ...paths,
    reused: false,
    source: "created",
    bookmark_path: bookmark,
    jobs_root: jobsRoot,
    session_binding: bindingId,
  };
}

/** @deprecated use createOrReuseSessionJob */
export function createJob(config: PluginConfig, label?: string, notes?: string): JobPaths {
  return createOrReuseSessionJob(config, { label, notes });
}

export function resolveJob(config: PluginConfig, jobId: string): JobPaths {
  if (!jobId || jobId.includes("..") || path.isAbsolute(jobId) || jobId.includes("/") || jobId.includes("\\")) {
    throw new Error(`Invalid job_id: ${jobId}`);
  }
  const root = path.join(resolveJobsRoot(config), jobId);
  if (!fs.existsSync(root)) {
    throw new Error(`Job not found: ${jobId}`);
  }
  return jobPaths(root, jobId);
}
