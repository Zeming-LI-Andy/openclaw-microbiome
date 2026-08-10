import { describe, expect, it } from "vitest";
import {
  detectDockerEnv,
  resolveReferences,
  resolveRefsMode,
} from "./resolve.js";
import type { UserRefsConfig } from "./types.js";

const sample: UserRefsConfig = {
  version: 1,
  refdb_root: {
    host_path: "/data/refdb",
    container_path: "/refdb",
  },
  references: {
    silva_ssu_nr99_seqs: {
      description: "SILVA 138.2 SSURef NR99 full-length reference sequences (.qza)",
      kind: "file",
      relative_path: "silva/silva-138.2-ssu-nr99-full-seqs.qza",
    },
    kneaddata_db_human_genome: {
      relative_path: "kneaddata/hg37dec_v0.1",
    },
    my_custom_db: {
      host_path: "/other/custom_db",
      container_path: "/refdb/custom/custom_db",
    },
  },
};

describe("resolveRefsMode", () => {
  it("respects explicit host/docker", () => {
    expect(resolveRefsMode("host")).toBe("host");
    expect(resolveRefsMode("docker")).toBe("docker");
  });

  it("auto uses docker when isDockerEnv true", () => {
    expect(resolveRefsMode("auto", true)).toBe("docker");
    expect(resolveRefsMode("auto", false)).toBe("host");
  });
});

describe("detectDockerEnv", () => {
  it("honors boolean override", () => {
    expect(detectDockerEnv(true)).toBe(true);
    expect(detectDockerEnv(false)).toBe(false);
  });
});

describe("resolveReferences", () => {
  it("host mode uses host_path + relative_path", () => {
    const r = resolveReferences(sample, { mode: "host" });
    expect(r.mode).toBe("host");
    expect(r.generated.references.silva_ssu_nr99_seqs?.path).toBe(
      "/data/refdb/silva/silva-138.2-ssu-nr99-full-seqs.qza",
    );
    expect(r.generated.references.kneaddata_db_human_genome?.path).toBe(
      "/data/refdb/kneaddata/hg37dec_v0.1",
    );
    expect(r.generated.references.my_custom_db?.path).toBe("/other/custom_db");
    expect(r.generated.references.silva_ssu_nr99_seqs?.description).toContain("SILVA");
    expect(r.generated.references.silva_ssu_nr99_seqs?.kind).toBe("file");
  });

  it("does not invent description/kind when user omits them", () => {
    const r = resolveReferences(sample, { mode: "host" });
    expect(r.generated.references.kneaddata_db_human_genome?.description).toBeUndefined();
    expect(r.generated.references.kneaddata_db_human_genome?.kind).toBeUndefined();
    expect(r.generated.references.kneaddata_db_human_genome?.path).toBe(
      "/data/refdb/kneaddata/hg37dec_v0.1",
    );
  });

  it("docker mode uses container_path + relative_path", () => {
    const r = resolveReferences(sample, { mode: "docker" });
    expect(r.mode).toBe("docker");
    expect(r.generated.references.silva_ssu_nr99_seqs?.path).toBe(
      "/refdb/silva/silva-138.2-ssu-nr99-full-seqs.qza",
    );
    expect(r.generated.references.my_custom_db?.path).toBe("/refdb/custom/custom_db");
    expect(r.recommendedExtraMounts).toContain("/data/refdb:/refdb:ro");
    expect(r.recommendedExtraMounts).toContain("/other/custom_db:/refdb/custom/custom_db:ro");
  });

  it("maps host_path under refdb_root to container path in docker mode", () => {
    const cfg: UserRefsConfig = {
      refdb_root: { host_path: "/data/refdb", container_path: "/refdb" },
      references: {
        card_db: { host_path: "/data/refdb/card" },
      },
    };
    const r = resolveReferences(cfg, { mode: "docker" });
    expect(r.generated.references.card_db?.path).toBe("/refdb/card");
  });

  it("warns when docker entry lacks container mapping", () => {
    const cfg: UserRefsConfig = {
      references: {
        orphan: { host_path: "/somewhere/db" },
      },
    };
    const r = resolveReferences(cfg, { mode: "docker" });
    expect(r.generated.references.orphan).toBeUndefined();
    expect(r.warnings.some((w) => w.includes("orphan"))).toBe(true);
  });
});
