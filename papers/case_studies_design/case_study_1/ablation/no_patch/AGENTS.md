# AGENTS.md — Microbiome OpenClaw workspace

## Session ↔ job

**One OpenClaw conversation = one `job_id`.**

1. **On conversation start — before anything else** (regardless of what the user
   said): call `mgx_create_job` once. Do not answer, plan, or run tools until
   this returns a `job_id`.
2. It creates or **reuses** this conversation’s job (per-session bookmark under
   `.microbiome/session_jobs/<sessionKey>` → new id). Different OpenClaw
   conversations get different `job_id`s.
3. All inputs/outputs for this conversation go under that job directory.
4. This conversation has exactly one `job_id`. Later `mgx_create_job` calls
   reuse it.

Resolve the job dir as:

`${OPENCLAW_JOBS_ROOT:-<jobsRoot>}/<job_id>/`

```
<job_id>/
  stage/                 # inputs
  analysis/<step>/       # outputs
  reproducibility/logs/
  job.json
```

## How you work

1. Read `TOOLS.md` and `CODING.md`. Follow `CODING.md` for how to run analysis.
2. Discover needed analysis tasks under **`plugin-skills/`**.
   Read the relevant `SKILL.md` when you take a step.
3. Use `registry/runtimes.yaml` and `registry/references.yaml` for envs and DB
   paths. If a needed path is missing, ask — do not invent paths.
4. Keep all I/O under this conversation’s job (`mgx_create_job` already ran at
   start).

## Plan then execute

When the user gives an analysis goal:

1. **Always create an analysis plan first** (ordered tasks, what “done” means).
   Ask only for blockers; otherwise state assumptions.
   Do **not** start heavy compute until the user confirms the plan
   (or clearly says to run).
2. After confirm: follow the `CODING.md` to execute the plan. **Keep the plan status
   updated in real time** as you go. Briefly report each step’s result + updated
   plan status, then continue the next unfinished task. Do not stop between tasks
   unless you hit a blocker that needs the user.
3. If a task fails and you confirm it cannot succeed: mark it **skipped** in the
   plan (with the reason), and mark any later tasks that **depend on it** as
   **skipped** too. Continue with remaining independent tasks. Do not invent
   results.
4. When no runnable tasks remain, summarize `job_id`, completed outputs, and
   what was skipped.

## Hard rules

1. **Every conversation must start with `mgx_create_job`** — first action, no
   exceptions based on the user’s first message.
2. All analysis I/O stays under the session job dir.
3. Shell analysis commands go through **`exec` only** (`TOOLS.md`) — never
   `terminal`.
4. **Always use absolute paths** for every file and directory you read, write,
   or pass to a tool (commands, scripts, configs, arguments). Never relative
   paths; never depend on cwd.
