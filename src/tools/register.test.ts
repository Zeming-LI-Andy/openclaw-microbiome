import fs from "node:fs";
import os from "node:os";
import path from "node:path";
import { afterEach, describe, expect, it } from "vitest";
import { loadCatalog, listToolIds } from "../catalog/load.js";
import { createOrReuseSessionJob } from "../runtime/job.js";
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
  it("creates once then reuses via bookmark", async () => {
    const root = tempRoot();
    const config = {
      jobsRoot: path.join(root, "jobs"),
      workspaceRoot: path.join(root, "workspace"),
      catalogDir: path.resolve(process.cwd(), "catalog"),
    };
    fs.mkdirSync(config.workspaceRoot, { recursive: true });

    const catalog = loadCatalog(config);
    const tools = Object.fromEntries(buildTools(catalog, () => config).map((t) => [t.name, t]));

    const first = await tools.mgx_create_job!.execute({ label: "study" });
    const a = first.details as { job_id: string; reused: boolean; bookmark_path: string };
    expect(a.reused).toBe(false);
    expect(fs.existsSync(a.bookmark_path)).toBe(true);
    expect(fs.readFileSync(a.bookmark_path, "utf8").trim()).toBe(a.job_id);

    const second = await tools.mgx_create_job!.execute({});
    const b = second.details as { job_id: string; reused: boolean; source: string };
    expect(b.reused).toBe(true);
    expect(b.job_id).toBe(a.job_id);
    expect(b.source).toBe("bookmark");
  });

  it("reuses OPENCLAW_SESSION_JOB_ID", () => {
    const root = tempRoot();
    const config = {
      jobsRoot: path.join(root, "jobs"),
      workspaceRoot: path.join(root, "workspace"),
    };
    fs.mkdirSync(config.workspaceRoot, { recursive: true });
    const created = createOrReuseSessionJob(config, { label: "env" });
    process.env.OPENCLAW_SESSION_JOB_ID = created.jobId;

    const again = createOrReuseSessionJob(config, {});
    expect(again.reused).toBe(true);
    expect(again.source).toBe("env");
    expect(again.jobId).toBe(created.jobId);
  });

  it("force_new mints another job", async () => {
    const root = tempRoot();
    const config = {
      jobsRoot: path.join(root, "jobs"),
      workspaceRoot: path.join(root, "workspace"),
      catalogDir: path.resolve(process.cwd(), "catalog"),
    };
    fs.mkdirSync(config.workspaceRoot, { recursive: true });
    const catalog = loadCatalog(config);
    const tools = Object.fromEntries(buildTools(catalog, () => config).map((t) => [t.name, t]));

    const first = await tools.mgx_create_job!.execute({});
    const second = await tools.mgx_create_job!.execute({ force_new: true });
    expect((second.details as { job_id: string }).job_id).not.toBe(
      (first.details as { job_id: string }).job_id,
    );
  });
});
