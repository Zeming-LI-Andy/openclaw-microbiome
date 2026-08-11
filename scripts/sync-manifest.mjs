import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";
import { parse as parseYaml } from "yaml";

const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "..");
const toolsDoc = parseYaml(fs.readFileSync(path.join(root, "catalog/tools.yaml"), "utf8"));
const toolIds = (toolsDoc.tools ?? []).map((t) => t.id);
const optionalMeta = {};
for (const t of toolsDoc.tools ?? []) {
  if (t.optional) {
    optionalMeta[t.id] = { optional: true };
  }
}

const manifest = {
  id: "microbiome",
  name: "Microbiome Tools",
  description:
    "Session job bootstrap for 16S/metagenomics (one OpenClaw session ↔ one job_id). Skills + Bash run the analysis.",
  version: "0.1.0",
  activation: {
    onStartup: true,
  },
  skills: ["./skills"],
  contracts: {
    tools: toolIds,
  },
  toolMetadata: optionalMeta,
  configSchema: {
    type: "object",
    additionalProperties: false,
    properties: {
      jobsRoot: {
        type: "string",
        description: "Root directory for analysis jobs (default: OPENCLAW_JOBS_ROOT or ./jobs).",
      },
      workspaceRoot: {
        type: "string",
        description:
          "Workspace checkout that stores .microbiome/session_jobs/ and registry/references.yaml.",
      },
      catalogDir: { type: "string" },
      refsConfig: {
        type: "string",
        description:
          "Path to user microbiome-refs.yaml (default: ~/.openclaw/microbiome-refs.yaml).",
      },
      refsMode: {
        type: "string",
        enum: ["auto", "docker", "host"],
        description:
          "Emit host or container paths into references.yaml (auto detects Docker).",
      },
    },
  },
};

const out = path.join(root, "openclaw.plugin.json");
fs.writeFileSync(out, JSON.stringify(manifest, null, 2) + "\n");
console.log(`Wrote ${out} with ${toolIds.length} tools`);
