# TOOLS.md — microbiome plugin

Plugin id: `microbiome`

## Plugin tool

| Tool | Purpose |
|------|---------|
| `mgx_create_job` | Create or reuse **this conversation’s** job; bookmark under `.microbiome/session_jobs/<sessionKey>` |

Other work uses native OpenClaw **Read** plus the shell **`exec`**.

## Shell execution (mandatory)

Run all analysis CLIs through **`exec`** (the OpenClaw shell tool).

- **Never use `terminal`** for analysis CLIs; it is an operator-facing UI PTY.
- Long jobs: call `exec` with **`yieldMs: 30000`** and **`timeout: 0`**; omit
  `background: true` so startup failures can return during the 30-second
  observation window. Keep the command itself in the foreground. Never use
  `nohup`, trailing `&`, `disown`, `setsid`, or equivalent shell detachment.
- Inspect the exec result. If it reports `status: "running"` with a valid
  `sessionId`, call `sessions_yield`; otherwise handle the returned completion,
  failure, or approval state directly. See `CODING.md`.

## Registries (read these)

### `registry/runtimes.yaml`

- Which tools/libraries exist
- Which `conda_env` to use (`mgx-base` is shared by `stats` and `host`)
- Optional `conda_executable` / `conda_prefix` (prefer PATH / `CONDA_EXE`)

```bash
conda run -n qiime2-amplicon-2024.10 --no-capture-output qiime --help
```

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

## Coding while analyzing

Read **`CODING.md`**: one analysis step at a time, small self-contained runs,
outputs under `analysis/<step>/`, `conda run -n …` from the registry. For
multi-hour CLIs, background `exec` + `sessions_yield`, then continue when
background exec ends (not automations babysitting).
