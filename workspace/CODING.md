# CODING.md — Analysis execution coding guide

Use with `registry/runtimes.yaml` and `registry/references.yaml`.

## Core principle: one analysis step at a time

Do **not** write a single mega-script that runs the whole pipeline end-to-end
and only then execute it.

Instead:

1. Pick **one** current step (usually one skill).
2. Write or assemble a **small, self-contained** command/script for that step.
3. **Run it now** (Bash / `conda run`).
4. Check exit status, logs, and outputs under this session’s job dir.
5. Only then move to the next step.

If a step needs Python **and** a CLI, or R **and** bash glue, use **separate
runs** (one language / one primary tool family per run), not one mixed blob.

```text
skill A → small run → verify artifacts
skill B → small run → verify artifacts
…
```

## Where code and data live

Session job (from `mgx_create_job`):

| Path | Use |
|------|-----|
| `stage/` | Inputs (FASTQ, manifests, metadata) |
| `analysis/<step>/` | Outputs for the **current** step only |
| `reproducibility/logs/` | Optional command logs you choose to keep |

- Prefer paths under **this session job**; avoid writing into the workspace
  checkout, `$HOME`, or `/tmp` as the primary output location.
- Prefer **absolute paths** once you know `job.root` / `stage` / `analysis`.
- Do not invent classifier or DB paths: read `registry/references.yaml`. If the
  needed path is missing, ask the user.

## Environment and tools

1. Read `registry/runtimes.yaml` for `conda_env` and allowed tools.
2. Run CLIs as:

   ```bash
   conda run -n <conda_env> --no-capture-output <tool> …
   ```

3. Use only tools/packages listed for that runtime (plus their normal runtime
   deps). Do **not** `pip install` / `conda install` / download large‑volume reference DBs
   as part of an analysis step unless the user explicitly asks.
4. For small online lookups (KEGG REST, etc.), keep them minimal and deliberate;
   do not turn “need a DB” into an unsupervised download.

## Language purity (per run)

| Intent | How to run |
|--------|------------|
| Python | One Python file or `python - <<'PY'` / `python script.py` — not “bash that embeds a huge `python -c`” |
| Shell / QIIME / metaphlan / … | Pure bash/`conda run` CLI pipeline for that step |
| R | Prefer `Rscript --vanilla your_step.R` or a short bash heredoc that only wraps Rscript |

Do not mix unrelated languages in one script “for convenience.” Split runs.

Bash tips when using conda:

- Prefer `conda run -n ENV --no-capture-output …` over `conda activate` in scripts.
- Prefer `set -eo pipefail`. Avoid `set -u` together with fragile activate hooks.
- Let the process **fail on error**; do not swallow CLI exit codes and continue.

## Multi-stage runs inside one step

Even within a single skill/step, avoid packing many **dependent** CLI or library
stages into one large script.

- If a later stage fails, first decide whether **upstream outputs are still valid**.
- When upstream outputs are valid: **rerun only the failed stage/samples**, and reuse
  existing intermediates under `analysis/<step>/`. Before skipping work, validate
  those files (exist, non-empty, expected format/schema — checksum when useful).
- When the failure is pipeline-level, upstream outputs are corrupted, or later
  stages depend on **changed parameters**: rerun from the start of that step and
  **replace stale** intermediate files.

## Parallelism (optional, inside one step)

Use parallelism only for **independent** work units inside the current step
(samples, files, features, comparisons) — never to mash sequential pipeline
stages together.

1. Identify the units and what parallelism each tool actually supports
   (process-level vs threads vs both).
2. Treat capacity as two levels:
   `concurrent units × threads per unit ≤ effective thread budget`.
3. **Reserve headroom**: do not schedule up to every logical core; leave room
   for I/O, the OS, and memory pressure.
4. Many small units → prefer **more concurrency, fewer threads each**.
   Few heavy units → prefer **fewer concurrent units, more threads each**.
5. Bound memory: `per-unit memory × concurrent units ≤ available headroom`.
   If unsure, start low and increase only after a successful run.
6. Set thread/worker counts **explicitly** in the command or code; do not rely
   on tool defaults.
7. **Do not** parallelize when units depend on each other, the tool is
   single-threaded, the workload is I/O- or memory-bound, or the job is too
   small to amortize worker startup.

## What “done” means for a step

A step is done when:

1. The run exited successfully (or you intentionally stopped with a clear reason).
2. Expected artifacts exist under `analysis/<step>/` (and are non-empty / sane).
3. You can summarize paths + key metrics for the user (and for the next skill).

Successful command exit alone is not enough if deliverables are missing.

## Data integrity (mandatory)

**Fabricating data is forbidden.**

- Do not invent counts, abundances, taxonomy labels, p-values, figures, tables,
  FASTQ/ASV contents, or “placeholder” analysis results and present them as real.
- Do not write fake `.qza` / tables / plots to look like a successful step.
- If inputs, DBs, or tools are missing, **stop and say what is missing** — do not
  simulate the run.
- Summaries must come only from real command output and real files under the
  session job (`stage/` / `analysis/`).
