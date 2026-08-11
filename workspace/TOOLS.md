# TOOLS.md — microbiome plugin

Plugin id: `microbiome`

## Plugin tool

| Tool | Purpose |
|------|---------|
| `mgx_create_job` | Create or reuse **this conversation’s** job; bookmark under `.microbiome/session_jobs/<sessionId>` |

Other work uses native OpenClaw **Read** plus the shell **`openclaw:core:exec`**.

## Shell execution (mandatory)

Run all analysis CLIs through **`openclaw:core:exec`** (the OpenClaw shell tool).

- Code Mode: `await tools.callValue("openclaw:core:exec", { command: "…" })`.
- Dialogue-layer `exec` (`{ language, code }`) is **JS/TS only** — never put a
  shell command there.
- **Never use `terminal`** for analysis CLIs; it is an operator-facing UI PTY.
- Long jobs: `background: true`, `timeout: 0`, completion wake; 
  status via **`openclaw:core:process`** when needed — see `CODING.md`.

## Registries (read these)

### `registry/runtimes.yaml`

- Which tools/libraries exist
- Which `conda_env` to use
- Optional `conda_executable` / `conda_prefix`

```bash
conda run -n qiime2-amplicon-2024.10 --no-capture-output qiime --help
```

### `registry/references.yaml`

Reference database paths for analysis steps. If a needed path is missing, ask
the user — do not invent paths.

## Session binding

Bound to the OpenClaw **conversation** (`sessionId`; fallback `sessionKey`):

1. `OPENCLAW_SESSION_JOB_ID` if set and the job dir exists  
2. else workspace `.microbiome/session_jobs/<sessionId>`  
3. else mint a new id and write that per-session bookmark  

Different conversations → different `job_id` directories. Same conversation →
reuse. `force_new: true` mints another job for the current conversation.

Jobs: `${OPENCLAW_JOBS_ROOT:-/data/output}/<job_id>/` (or plugin `jobsRoot`).

## Skills

Under `skills/<name>/SKILL.md`. See `AGENTS.md` for the skill map.

Some skills include a `scripts/` folder with **reference** helpers (CLI args /
env for paths — no hardwired machine DBs). Copy or adapt them under the session
job; adjust to the real inputs and `registry/references.yaml` resolutions.

Local DB annotation: `shotgun-eggnog`, `shotgun-vfdb`, `shotgun-rgi` (one skill
per reference DB). REST skills (`annotation-kegg`, `annotation-uniprot`,
`annotation-gene-ontology`, `annotation-ncbi-gene`, `annotation-metacyc`,
`annotation-eggnog-api`) document API patterns. Public fetch: `sra-search`
(SRA metadata), `ncbi-assembly-proteins` (Assembly proteins).

## Coding while analyzing

Read **`CODING.md`**: one analysis step at a time, small self-contained runs,
outputs under `analysis/<step>/`, `conda run -n …` from the registry. For
multi-hour CLIs, background `openclaw:core:exec` + exit wake (not cron
babysitting).
