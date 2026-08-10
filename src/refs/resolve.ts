import fs from "node:fs";
import os from "node:os";
import path from "node:path";
import YAML from "yaml";
import { STANDARD_REFERENCE_CATALOG } from "./catalog.js";
import type {
  GeneratedReferenceEntry,
  GeneratedReferences,
  RefsMode,
  ResolveRefsOptions,
  ResolveRefsResult,
  ResolvedRefsMode,
  UserReferenceEntry,
  UserRefsConfig,
} from "./types.js";

const DEFAULT_CONTAINER_ROOT = "/refdb";

/** Expand leading `~` to the user home directory. */
export function expandHome(p: string): string {
  if (p === "~") return os.homedir();
  if (p.startsWith("~/") || p.startsWith("~\\")) {
    return path.join(os.homedir(), p.slice(2));
  }
  return p;
}

export function defaultRefsConfigPath(): string {
  return path.join(os.homedir(), ".openclaw", "microbiome-refs.yaml");
}

/** Detect Docker / OpenClaw gateway container environment. */
export function detectDockerEnv(override?: boolean): boolean {
  if (typeof override === "boolean") return override;
  if (process.env.OPENCLAW_STATE_DIR === "/home/node/.openclaw") return true;
  try {
    return fs.existsSync("/.dockerenv");
  } catch {
    return false;
  }
}

export function resolveRefsMode(
  mode: RefsMode | undefined,
  isDockerEnv?: boolean,
): ResolvedRefsMode {
  const m = mode ?? "auto";
  if (m === "docker" || m === "host") return m;
  return detectDockerEnv(isDockerEnv) ? "docker" : "host";
}

function joinPosix(root: string, rel: string): string {
  const cleanRoot = root.replace(/\/+$/, "");
  const cleanRel = rel.replace(/^\/+/, "");
  return `${cleanRoot}/${cleanRel}`;
}

function parseUserRefs(raw: unknown): UserRefsConfig {
  if (!raw || typeof raw !== "object" || Array.isArray(raw)) {
    throw new Error("microbiome-refs.yaml must be a YAML mapping");
  }
  return raw as UserRefsConfig;
}

export function loadUserRefsConfig(filePath: string): UserRefsConfig {
  const text = fs.readFileSync(filePath, "utf8");
  return parseUserRefs(YAML.parse(text));
}

function resolveEntryPath(params: {
  id: string;
  entry: UserReferenceEntry;
  mode: ResolvedRefsMode;
  rootHost?: string;
  rootContainer?: string;
  warnings: string[];
}): string | null {
  const { id, entry, mode, rootHost, rootContainer, warnings } = params;

  if (entry.relative_path) {
    if (!rootHost && mode === "host") {
      warnings.push(`${id}: relative_path set but refdb_root.host_path is missing`);
      return null;
    }
    if (mode === "host") {
      return joinPosix(rootHost!, entry.relative_path);
    }
    const containerRoot = rootContainer ?? DEFAULT_CONTAINER_ROOT;
    return joinPosix(containerRoot, entry.relative_path);
  }

  if (mode === "host") {
    if (!entry.host_path) {
      warnings.push(`${id}: missing host_path or relative_path`);
      return null;
    }
    return entry.host_path;
  }

  // docker
  if (entry.container_path) {
    return entry.container_path;
  }
  if (entry.host_path && rootHost && rootContainer) {
    const host = entry.host_path.replace(/\/+$/, "");
    const root = rootHost.replace(/\/+$/, "");
    if (host === root || host.startsWith(`${root}/`)) {
      const rel = host === root ? "" : host.slice(root.length + 1);
      return rel ? joinPosix(rootContainer, rel) : rootContainer.replace(/\/+$/, "") || "/";
    }
  }
  warnings.push(
    `${id}: docker mode needs container_path (or relative_path under refdb_root)`,
  );
  return null;
}

function collectRecommendedMounts(cfg: UserRefsConfig): string[] {
  const mounts: string[] = [];
  const seen = new Set<string>();

  const add = (host: string, guest: string) => {
    const spec = `${host}:${guest}:ro`;
    if (seen.has(spec)) return;
    seen.add(spec);
    mounts.push(spec);
  };

  if (cfg.refdb_root?.host_path) {
    add(
      cfg.refdb_root.host_path.replace(/\/+$/, ""),
      (cfg.refdb_root.container_path ?? DEFAULT_CONTAINER_ROOT).replace(/\/+$/, "") ||
        DEFAULT_CONTAINER_ROOT,
    );
  }

  for (const [id, entry] of Object.entries(cfg.references ?? {})) {
    if (entry.relative_path) continue;
    if (entry.host_path && entry.container_path) {
      add(entry.host_path.replace(/\/+$/, ""), entry.container_path.replace(/\/+$/, ""));
      continue;
    }
    if (entry.host_path && !entry.container_path && !cfg.refdb_root) {
      // cannot recommend without guest path
      void id;
    }
  }

  return mounts;
}

/** Resolve user refs config into agent-facing references + recommended mounts. */
export function resolveReferences(
  cfg: UserRefsConfig,
  options: ResolveRefsOptions = {},
): ResolveRefsResult {
  const mode = resolveRefsMode(options.mode, options.isDockerEnv);
  const catalog = options.catalog ?? STANDARD_REFERENCE_CATALOG;
  const warnings: string[] = [];
  const references: Record<string, GeneratedReferenceEntry> = {};

  const rootHost = cfg.refdb_root?.host_path;
  const rootContainer = cfg.refdb_root?.container_path ?? DEFAULT_CONTAINER_ROOT;

  for (const [id, entry] of Object.entries(cfg.references ?? {})) {
    if (!entry || typeof entry !== "object") {
      warnings.push(`${id}: invalid entry`);
      continue;
    }
    const resolvedPath = resolveEntryPath({
      id,
      entry,
      mode,
      rootHost,
      rootContainer,
      warnings,
    });
    if (!resolvedPath) continue;

    const fromCatalog = catalog[id];
    const out: GeneratedReferenceEntry = { path: resolvedPath };
    const description = entry.description ?? fromCatalog?.description;
    const kind = entry.kind ?? fromCatalog?.kind;
    if (description) out.description = description;
    if (kind) out.kind = kind;
    references[id] = out;
  }

  return {
    mode,
    generated: { references },
    recommendedExtraMounts: collectRecommendedMounts(cfg),
    warnings,
  };
}

export function emptyGeneratedReferences(): GeneratedReferences {
  return { references: {} };
}
