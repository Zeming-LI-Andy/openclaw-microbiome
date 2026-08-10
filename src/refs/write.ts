import fs from "node:fs";
import path from "node:path";
import YAML from "yaml";
import type { GeneratedReferences } from "./types.js";

const HEADER = `# Reference database paths for analysis.
# If a needed path is missing, ask the user — do not invent paths.
`;

export function formatGeneratedReferencesYaml(generated: GeneratedReferences): string {
  const body = YAML.stringify(
    { references: generated.references },
    { lineWidth: 100, defaultKeyType: "PLAIN", defaultStringType: "QUOTE_DOUBLE" },
  );
  return `${HEADER}\n${body}`;
}

/** Write workspace/registry/references.yaml (creates registry/ as needed). */
export function writeGeneratedReferences(
  workspaceRoot: string,
  generated: GeneratedReferences,
): string {
  const registryDir = path.join(workspaceRoot, "registry");
  fs.mkdirSync(registryDir, { recursive: true });
  const outPath = path.join(registryDir, "references.yaml");
  fs.writeFileSync(outPath, formatGeneratedReferencesYaml(generated), "utf8");
  return outPath;
}
