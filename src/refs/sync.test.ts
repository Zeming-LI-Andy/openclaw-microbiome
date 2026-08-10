import fs from "node:fs";
import os from "node:os";
import path from "node:path";
import { afterEach, describe, expect, it } from "vitest";
import { syncReferences } from "./sync.js";

const tmpDirs: string[] = [];

afterEach(() => {
  for (const dir of tmpDirs.splice(0)) {
    fs.rmSync(dir, { recursive: true, force: true });
  }
});

function tempRoot(): string {
  const dir = fs.mkdtempSync(path.join(os.tmpdir(), "mgx-refs-"));
  tmpDirs.push(dir);
  return dir;
}

describe("syncReferences", () => {
  it("writes empty references when config missing", () => {
    const root = tempRoot();
    const workspaceRoot = path.join(root, "workspace");
    const logs: string[] = [];
    const result = syncReferences({
      refsConfigPath: path.join(root, "missing.yaml"),
      workspaceRoot,
      log: {
        info: (m) => logs.push(String(m)),
        warn: (m) => logs.push(String(m)),
        error: (m) => logs.push(String(m)),
      },
    });
    expect(result.missingConfig).toBe(true);
    expect(fs.existsSync(result.outputPath)).toBe(true);
    const text = fs.readFileSync(result.outputPath, "utf8");
    expect(text).toContain("references:");
    expect(text).toMatch(/ask the user/i);
  });

  it("generates host paths from example-shaped yaml", () => {
    const root = tempRoot();
    const refsPath = path.join(root, "microbiome-refs.yaml");
    const workspaceRoot = path.join(root, "workspace");
    fs.writeFileSync(
      refsPath,
      `
version: 1
refdb_root:
  host_path: /data/refdb
  container_path: /refdb
references:
  silva_ssu_nr99_seqs:
    relative_path: silva/silva-138.2-ssu-nr99-full-seqs.qza
`,
      "utf8",
    );

    const result = syncReferences({
      refsConfigPath: refsPath,
      workspaceRoot,
      mode: "host",
      log: { info: () => {}, warn: () => {}, error: () => {} },
    });

    expect(result.missingConfig).toBe(false);
    expect(result.generated.references.silva_ssu_nr99_seqs?.path).toBe(
      "/data/refdb/silva/silva-138.2-ssu-nr99-full-seqs.qza",
    );
    const text = fs.readFileSync(result.outputPath, "utf8");
    expect(text).toContain("/data/refdb/silva/");
    expect(text).not.toContain("mount_path");
    expect(text).not.toContain("local_path");
  });
});
