export type PreferRuntime = "docker" | "conda";

export type RefsMode = "auto" | "docker" | "host";

export type PluginConfig = {
  jobsRoot?: string;
  /** Workspace checkout that stores `.current_job_id` (default: cwd / OPENCLAW_WORKSPACE). */
  workspaceRoot?: string;
  preferRuntime?: PreferRuntime;
  condaExecutable?: string;
  catalogDir?: string;
  dryRun?: boolean;
  /** Path to user microbiome-refs.yaml (default: ~/.openclaw/microbiome-refs.yaml). */
  refsConfig?: string;
  /** host | docker | auto — which path namespace to write into references.yaml. */
  refsMode?: RefsMode;
};

export type RuntimeSpec = {
  id: string;
  description?: string;
  conda_env?: string;
  image?: string;
  image_conda_env?: string;
  allowlist?: string[];
};

export type JsonSchema = {
  type?: string;
  description?: string;
  properties?: Record<string, JsonSchema>;
  required?: string[];
  additionalProperties?: boolean;
  enum?: Array<string | number | boolean>;
  items?: JsonSchema;
  default?: unknown;
};

export type OptionalArgvRule = {
  when: string;
  equals?: unknown;
  args: string[];
};

export type ToolKind = "project";

export type ToolSpec = {
  id: string;
  kind: ToolKind;
  description: string;
  runtime?: string;
  optional?: boolean;
  network?: boolean;
  parameters: JsonSchema;
  argv?: string[];
  optional_argv?: OptionalArgvRule[];
};

export type Catalog = {
  runtimes: Record<string, RuntimeSpec>;
  tools: ToolSpec[];
};

export type JobPaths = {
  jobId: string;
  root: string;
  stage: string;
  analysis: string;
  reproducibility: string;
  logs: string;
};

export type RunRequest = {
  argv: string[];
  runtime: RuntimeSpec;
  job: JobPaths;
  toolId: string;
  network?: boolean;
  workdir?: string;
  dryRun?: boolean;
};

export type RunResult = {
  ok: boolean;
  exitCode: number | null;
  backend: "docker" | "conda" | "dry-run" | "host";
  image?: string;
  condaEnv?: string;
  argv: string[];
  stdout: string;
  stderr: string;
  logPath?: string;
  durationMs: number;
};
