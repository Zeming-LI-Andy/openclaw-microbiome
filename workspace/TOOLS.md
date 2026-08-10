# TOOLS.md — microbiome plugin

Plugin id: `microbiome`

## Plugin tool

| Tool | Purpose |
|------|---------|
| `mgx_create_job` | Create or reuse the **session** job; write `.current_job_id` |

Other work uses native OpenClaw **Read** / **Bash** (`exec`). Long-running
analysis steps should use **background `exec`** (`background: true`,
`timeout: 0`) and resume on **completion wake** (`notifyOnExit`); manage with
**`process`** only for on-demand status — see `CODING.md`.

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

1. `OPENCLAW_SESSION_JOB_ID` if set  
2. else `.current_job_id`  
3. else mint new id via `mgx_create_job`

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
multi-hour CLIs, background `exec` + exit wake (not cron babysitting).
