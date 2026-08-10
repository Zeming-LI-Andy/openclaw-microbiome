/** User-facing refsMode: which path namespace to emit into references.yaml. */
export type RefsMode = "auto" | "docker" | "host";

/** Resolved runtime mode after auto-detection. */
export type ResolvedRefsMode = "docker" | "host";

export type RefKind = "file" | "directory";

/** Optional whole-tree bind: host refdb root → container path. */
export type RefdbRootConfig = {
  host_path: string;
  /** Default `/refdb` when omitted. */
  container_path?: string;
};

/** One user-declared reference in microbiome-refs.yaml. */
export type UserReferenceEntry = {
  /** Path relative to refdb_root (preferred). */
  relative_path?: string;
  /** Absolute host path (tree-exception or standalone). */
  host_path?: string;
  /** Absolute container path when not under refdb_root. */
  container_path?: string;
  /** Optional; copied into generated references.yaml if set. */
  description?: string;
  /** Optional; copied into generated references.yaml if set. */
  kind?: RefKind;
};

/** Parsed microbiome-refs.yaml. */
export type UserRefsConfig = {
  version?: number;
  refdb_root?: RefdbRootConfig;
  references?: Record<string, UserReferenceEntry>;
};

/** One entry written to workspace/registry/references.yaml. */
export type GeneratedReferenceEntry = {
  description?: string;
  kind?: RefKind;
  path: string;
};

export type GeneratedReferences = {
  references: Record<string, GeneratedReferenceEntry>;
};

export type ResolveRefsOptions = {
  /** Explicit mode; default auto. */
  mode?: RefsMode;
  /** Override auto docker detection (tests). */
  isDockerEnv?: boolean;
};

export type ResolveRefsResult = {
  mode: ResolvedRefsMode;
  generated: GeneratedReferences;
  /** e.g. `/data/refdb:/refdb:ro` for OPENCLAW_EXTRA_MOUNTS. */
  recommendedExtraMounts: string[];
  warnings: string[];
};

export type SyncReferencesOptions = {
  /** Absolute or ~-expanded path to microbiome-refs.yaml. */
  refsConfigPath: string;
  /** Workspace root that contains registry/. */
  workspaceRoot: string;
  mode?: RefsMode;
  isDockerEnv?: boolean;
  /** Logger; defaults to console. */
  log?: Pick<Console, "info" | "warn" | "error">;
};
