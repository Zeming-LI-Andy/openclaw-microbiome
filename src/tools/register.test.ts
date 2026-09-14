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
    const session = { sessionKey: "agent:main:dashboard:conv-aaaa-1111" };

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
    expect(a.session_binding).toBe(session.sessionKey);
    expect(a.bookmark_path).toBe(sessionBookmarkPath(config, session.sessionKey));
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

    const a = await tools.mgx_create_job!.execute({}, { sessionKey: "agent:main:dashboard:session-a" });
    const b = await tools.mgx_create_job!.execute({}, { sessionKey: "agent:main:dashboard:session-b" });
    expect((a.details as { job_id: string }).job_id).not.toBe(
      (b.details as { job_id: string }).job_id,
    );
    expect((a.details as { reused: boolean }).reused).toBe(false);
    expect((b.details as { reused: boolean }).reused).toBe(false);
  });

  it("reuses OPENCLAW_SESSION_JOB_ID only without session binding", () => {
    const root = tempRoot();
    const config = {
      jobsRoot: path.join(root, "jobs"),
      workspaceRoot: path.join(root, "workspace"),
    };
    fs.mkdirSync(config.workspaceRoot, { recursive: true });
    const created = createOrReuseSessionJob(config, {
      label: "env",
    });
    process.env.OPENCLAW_SESSION_JOB_ID = created.jobId;

    const again = createOrReuseSessionJob(config, {});
    expect(again.reused).toBe(true);
    expect(again.source).toBe("env");
    expect(again.jobId).toBe(created.jobId);
  });

  it("ignores OPENCLAW_SESSION_JOB_ID when session binding is present", () => {
    const root = tempRoot();
    const config = {
      jobsRoot: path.join(root, "jobs"),
      workspaceRoot: path.join(root, "workspace"),
    };
    fs.mkdirSync(config.workspaceRoot, { recursive: true });
    const shared = createOrReuseSessionJob(config, {
      label: "shared",
    });
    process.env.OPENCLAW_SESSION_JOB_ID = shared.jobId;

    const a = createOrReuseSessionJob(config, { session: { sessionKey: "agent:main:dashboard:sess-a" } });
    const b = createOrReuseSessionJob(config, { session: { sessionKey: "agent:main:dashboard:sess-b" } });
    expect(a.jobId).not.toBe(shared.jobId);
    expect(b.jobId).not.toBe(shared.jobId);
    expect(a.jobId).not.toBe(b.jobId);
    expect(a.source).toBe("created");
    expect(b.source).toBe("created");
  });

  it("same session always reuses even if force_new is passed", async () => {
    const root = tempRoot();
    const config = {
      jobsRoot: path.join(root, "jobs"),
      workspaceRoot: path.join(root, "workspace"),
      catalogDir: path.resolve(process.cwd(), "catalog"),
    };
    fs.mkdirSync(config.workspaceRoot, { recursive: true });
    const catalog = loadCatalog(config);
    const tools = Object.fromEntries(buildTools(catalog, () => config).map((t) => [t.name, t]));
    const session = { sessionKey: "agent:main:dashboard:sess-force" };

    const first = await tools.mgx_create_job!.execute({}, session);
    const second = await tools.mgx_create_job!.execute({ force_new: true }, session);
    const a = first.details as { job_id: string };
    const b = second.details as { job_id: string; reused: boolean };
    expect(b.job_id).toBe(a.job_id);
    expect(b.reused).toBe(true);
  });

  it("reuses the same job when only the rotating sessionId would have changed", () => {
    const root = tempRoot();
    const config = {
      jobsRoot: path.join(root, "jobs"),
      workspaceRoot: path.join(root, "workspace"),
    };
    fs.mkdirSync(config.workspaceRoot, { recursive: true });
    const sessionKey = "agent:main:dashboard:4531d4a1-cacc-4558-9aa6-3d5f0968ddb0";

    const first = createOrReuseSessionJob(config, { session: { sessionKey } });
    const second = createOrReuseSessionJob(config, { session: { sessionKey } });
    expect(first.reused).toBe(false);
    expect(second.reused).toBe(true);
    expect(second.jobId).toBe(first.jobId);
    expect(second.session_binding).toBe(sessionKey);
  });

  it("ignores sessionId-only context and does not treat it as a conversation binding", () => {
    const root = tempRoot();
    const config = {
      jobsRoot: path.join(root, "jobs"),
      workspaceRoot: path.join(root, "workspace"),
    };
    fs.mkdirSync(config.workspaceRoot, { recursive: true });
    const created = createOrReuseSessionJob(config, {});
    process.env.OPENCLAW_SESSION_JOB_ID = created.jobId;

    const again = createOrReuseSessionJob(config, {
      session: { sessionKey: undefined },
    });
    expect(again.reused).toBe(true);
    expect(again.source).toBe("env");
    expect(again.jobId).toBe(created.jobId);
  });
});
