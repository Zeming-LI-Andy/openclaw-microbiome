import { Type } from "typebox";
import type { Catalog, PluginConfig } from "../runtime/types.js";
import { createOrReuseSessionJob } from "../runtime/job.js";

export const projectToolIds = ["mgx_create_job"] as const;

export function isProjectTool(id: string): boolean {
  return (projectToolIds as readonly string[]).includes(id);
}

export async function executeProjectTool(
  toolId: string,
  params: Record<string, unknown>,
  config: PluginConfig,
  _catalog: Catalog,
): Promise<unknown> {
  if (toolId !== "mgx_create_job") {
    throw new Error(`Unknown project tool: ${toolId}`);
  }

  const result = createOrReuseSessionJob(config, {
    label: typeof params.label === "string" ? params.label : undefined,
    notes: typeof params.notes === "string" ? params.notes : undefined,
    forceNew: Boolean(params.force_new),
  });

  return {
    job_id: result.jobId,
    reused: result.reused,
    source: result.source,
    root: result.root,
    stage: result.stage,
    analysis: result.analysis,
    reproducibility: result.reproducibility,
    jobs_root: result.jobs_root,
    bookmark_path: result.bookmark_path,
    session: {
      one_session_one_job: true,
      env_var: "OPENCLAW_SESSION_JOB_ID",
      hint: result.reused
        ? "Reusing this session's job_id. Keep all analysis I/O under this job directory."
        : "New session job created. Remember job_id for this conversation; write all outputs under root/stage/analysis.",
    },
  };
}

export const projectParameterSchemas = {
  mgx_create_job: Type.Object({
    label: Type.Optional(Type.String({ description: "Short human label." })),
    notes: Type.Optional(Type.String({ description: "Optional notes." })),
    force_new: Type.Optional(
      Type.Boolean({ description: "Mint a new job even if the session already has one." }),
    ),
  }),
} as const;
