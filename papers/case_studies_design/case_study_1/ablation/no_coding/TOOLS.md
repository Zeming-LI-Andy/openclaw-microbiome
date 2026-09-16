# TOOLS.md — microbiome plugin

Plugin id: `microbiome`

## Plugin tool

| Tool | Purpose |
|------|---------|
| `mgx_create_job` | Create or reuse **this conversation’s** job; bookmark under `.microbiome/session_jobs/<sessionKey>` |

Other work uses native OpenClaw **Read** plus the shell **`exec`**. Never use
`terminal` for analysis CLIs.

## Registries (read these)

### `registry/runtimes.yaml`

Which tools/libraries exist and which `conda_env` to use (`mgx-base` is shared
by `stats` and `host`).

### `registry/references.yaml`

Reference database paths for analysis steps. If a needed path is missing, ask
the user — do not invent paths.

## Session binding

Bound to the OpenClaw **conversation** (`sessionKey`):

1. workspace `.microbiome/session_jobs/<sessionKey>` if present → reuse that job
2. else mint a new id and write that per-session bookmark

Different conversations → different `job_id`s. Same conversation →
always reuse the same `job_id`, including after sessionId rotation
(rewind / reset).

Jobs: `${OPENCLAW_JOBS_ROOT:-/data/output}/<job_id>/` (or plugin `jobsRoot`).

## Skills

Use **plugin-shipped** skills only: `plugin-skills/<name>/SKILL.md`
(`$OPENCLAW_STATE_DIR/plugin-skills`). Discover needed tasks there (see
`AGENTS.md`).

Do **not** create or edit skills during analysis (`skill_workshop` / writing
under `workspace/skills/`). Analysis follows existing plugin skills.

Some skills include a `scripts/` folder with **reference** helpers (CLI args /
env for paths — no hardwired machine DBs). Copy or adapt them under the session
job; adjust to the real inputs and `registry/references.yaml` resolutions.

Local DB annotation: `shotgun-eggnog`, `shotgun-vfdb`, `shotgun-rgi`,
`shotgun-bakta`, `shotgun-gapseq`, `shotgun-gutsmash`, `shotgun-antismash`
(one skill per tool / reference DB). REST skills (`annotation-kegg`, `annotation-uniprot`,
`annotation-gene-ontology`, `annotation-ncbi-gene`, `annotation-metacyc`,
`annotation-eggnog-api`) document API patterns. Public fetch: `sra-search`
(SRA metadata), `ncbi-assembly-proteins` (Assembly proteins).
