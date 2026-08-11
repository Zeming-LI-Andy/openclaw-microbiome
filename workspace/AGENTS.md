# AGENTS.md — Microbiome OpenClaw workspace

## Session ↔ job

**One OpenClaw conversation = one `job_id`.**

1. At the start of an analysis session, call `mgx_create_job` once.
2. It creates or **reuses** this conversation’s job (`OPENCLAW_SESSION_JOB_ID`
   → per-session bookmark under `.microbiome/session_jobs/<sessionId>` → new
   id). Different OpenClaw conversations get different `job_id`s.
3. All inputs/outputs for this conversation go under that job directory.
4. Do not mint a second job mid-chat unless the user explicitly wants a new
   analysis (`force_new: true`).

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

1. `mgx_create_job` → remember `job_id` / paths.
2. Follow `CODING.md` (one step → run → verify → next).
3. Read **`registry/runtimes.yaml`** for CLIs/libraries and `conda_env`.
4. Read **`registry/references.yaml`** for reference DB paths when a step needs
   them. If a needed path is missing, ask the user — do not invent paths.
5. Read `skills/<step>/SKILL.md` for the step procedure.
6. Run with **`openclaw:core:exec`**: `conda run -n <conda_env>
   --no-capture-output …` For long steps, use **background
   `openclaw:core:exec` + `timeout: 0`** and completion wake (see `CODING.md` →
   Long-running steps) — do not block the turn for hours.
7. Write under `analysis/<step>/` in **this** session job.

## Session startup

1. Read `TOOLS.md` and `CODING.md`.
2. Skim `registry/runtimes.yaml` (and `references.yaml` when DBs are needed).
3. If no job yet, `mgx_create_job`.
4. Prefer the returned `job_id` (and `root` / `stage` / `analysis`) for the
   rest of the session.

## Hard rules

1. All analysis I/O stays under the session job dir.
2. Ask before provenance-sensitive choices when unknown.
3. Never invent classifier / DB paths — read `registry/references.yaml`, or ask.
4. Execute **one analysis step at a time** (see `CODING.md`); do not ship a
   whole-pipeline script and run it once at the end.
5. Long CLIs: background + exit wake — not cron/sleep poll loops (`CODING.md`).
6. Never use `terminal` for analysis CLIs; shell commands go through
   `openclaw:core:exec` only (`TOOLS.md`).

## Skill map (high level)

**16S:** `16s-import` → `16s-denoise-dada2` → `16s-feature-summarize` →
`16s-taxonomy` → `16s-phylogeny` → `16s-diversity` → optional `16s-export` /
`16s-picrust2`

**Shotgun:** `shotgun-kneaddata` → `shotgun-metaphlan` → optional `shotgun-humann`
→ optional `shotgun-gene-catalog` / `shotgun-eggnog` / `shotgun-vfdb` /
`shotgun-rgi` / `shotgun-aviary`

**Public data:** `sra-search` (SRA metadata), `ncbi-assembly-proteins` (Assembly
`.faa` download)

**Stats / annotation:** `stats-diversity`, `stats-differential-abundance`,
`stats-enrichment`, `annotation-kegg`, `annotation-uniprot`,
`annotation-gene-ontology`, `annotation-ncbi-gene`, `annotation-metacyc`,
`annotation-eggnog-api`

Skill `scripts/` are **reference** helpers (paths like `scripts/foo.py` are
relative to that skill). **Copy/adapt** into the session job before running;
do not treat the skill tree as the run cwd or as a fixed pipeline.
