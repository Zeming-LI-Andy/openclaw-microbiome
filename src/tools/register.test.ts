import fs from "node:fs";
import os from "node:os";
import path from "node:path";
import { afterEach, describe, expect, it } from "vitest";
import { loadCatalog, listToolIds } from "../catalog/load.js";
import { createOrReuseSessionJob, sessionBookmarkPath } from "../runtime/job.js";
import { buildTools } from "./register.js";

const tmpDirs: string[] = [];

afterEach(() => {
  for (const dir of tmpDirs.splice(0)) {
    fs.rmSync(dir, { recursive: true, force: true });
  }
  delete process.env.OPENCLAW_SESSION_JOB_ID;
});

function tempRoot(): string {
  const dir = fs.mkdtempSync(path.join(os.tmpdir(), "mgx-test-"));
  tmpDirs.push(dir);
  return dir;
}

describe("catalog", () => {
  it("registers only mgx_create_job", () => {
    const catalog = loadCatalog({
      catalogDir: path.resolve(process.cwd(), "catalog"),
    });
    expect(listToolIds(catalog)).toEqual(["mgx_create_job"]);
  });
});

describe("session job", () => {
  it("creates once then reuses via per-session bookmark", async () => {
    const root = tempRoot();
    const config = {
      jobsRoot: path.join(root, "jobs"),
      workspaceRoot: path.join(root, "workspace"),
      catalogDir: path.resolve(process.cwd(), "catalog"),
    };
    fs.mkdirSync(config.workspaceRoot, { recursive: true });
    const session = { sessionId: "conv-aaaa-1111" };

    const catalog = loadCatalog(config);
    const tools = Object.fromEntries(buildTools(catalog, () => config).map((t) => [t.name, t]));

    const first = await tools.mgx_create_job!.execute({ label: "study" }, session);
    const a = first.details as {
      job_id: string;
      reused: boolean;
      bookmark_path: string;
      session_binding: string;
    };
    expect(a.reused).toBe(false);
    expect(a.session_binding).toBe(session.sessionId);
    expect(a.bookmark_path).toBe(sessionBookmarkPath(config, session.sessionId));
    expect(fs.readFileSync(a.bookmark_path, "utf8").trim()).toBe(a.job_id);

    const second = await tools.mgx_create_job!.execute({}, session);
    const b = second.details as { job_id: string; reused: boolean; source: string };
    expect(b.reused).toBe(true);
    expect(b.job_id).toBe(a.job_id);
    expect(b.source).toBe("session");
  });

  it("different sessions get different job_ids", async () => {
    const root = tempRoot();
    const config = {
      jobsRoot: path.join(root, "jobs"),
      workspaceRoot: path.join(root, "workspace"),
      catalogDir: path.resolve(process.cwd(), "catalog"),
    };
    fs.mkdirSync(config.workspaceRoot, { recursive: true });
    const catalog = loadCatalog(config);
    const tools = Object.fromEntries(buildTools(catalog, () => config).map((t) => [t.name, t]));

    const a = await tools.mgx_create_job!.execute({}, { sessionId: "session-a" });
    const b = await tools.mgx_create_job!.execute({}, { sessionId: "session-b" });
    expect((a.details as { job_id: string }).job_id).not.toBe(
      (b.details as { job_id: string }).job_id,
    );
    expect((a.details as { reused: boolean }).reused).toBe(false);
    expect((b.details as { reused: boolean }).reused).toBe(false);
  });

  it("reuses OPENCLAW_SESSION_JOB_ID", () => {
    const root = tempRoot();
    const config = {
      jobsRoot: path.join(root, "jobs"),
      workspaceRoot: path.join(root, "workspace"),
    };
    fs.mkdirSync(config.workspaceRoot, { recursive: true });
    const created = createOrReuseSessionJob(config, {
      label: "env",
      session: { sessionId: "sess-env" },
    });
    process.env.OPENCLAW_SESSION_JOB_ID = created.jobId;

    const again = createOrReuseSessionJob(config, {
      session: { sessionId: "sess-env" },
    });
    expect(again.reused).toBe(true);
    expect(again.source).toBe("env");
    expect(again.jobId).toBe(created.jobId);
  });

  it("force_new mints another job for the same session", async () => {
    const root = tempRoot();
    const config = {
      jobsRoot: path.join(root, "jobs"),
      workspaceRoot: path.join(root, "workspace"),
      catalogDir: path.resolve(process.cwd(), "catalog"),
    };
    fs.mkdirSync(config.workspaceRoot, { recursive: true });
    const catalog = loadCatalog(config);
    const tools = Object.fromEntries(buildTools(catalog, () => config).map((t) => [t.name, t]));
    const session = { sessionId: "sess-force" };

    const first = await tools.mgx_create_job!.execute({}, session);
    const second = await tools.mgx_create_job!.execute({ force_new: true }, session);
    expect((second.details as { job_id: string }).job_id).not.toBe(
      (first.details as { job_id: string }).job_id,
    );
  });
});
