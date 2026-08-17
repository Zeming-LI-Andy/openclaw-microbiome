---
name: shotgun-gutsmash
description: >
  Detect anaerobic gut metabolic gene clusters with gutSMASH (antiSMASH 5-era fork).
runtime: gutsmash
conda_env: gutsmash
tools:
  - gutsmash
  - python
  - prodigal
---

# Gut metabolic gene clusters (gutSMASH)

## Runtime

| Field | Value |
|-------|-------|
| Runtime id | `gutsmash` |
| Conda env | `gutsmash` |

DB: look up `gutsmash_db` in `registry/references.yaml`. If missing, ask the
user — do not invent. Pass that directory as `--databases`.

Never run `download-antismash-databases`. smCOGs / KnownClusterBlast for this
tool live inside the conda package, not under `gutsmash_db`.

Run with `conda run -n gutsmash --no-capture-output gutsmash …` (the `gutsmash`
CLI is this env’s entry point).

## Reference script (`scripts/`)

Reference (path relative to this skill): `scripts/run_gutsmash.py`.

**Copy/adapt** it under the session job; do not run against the skill tree as
cwd. After copying to e.g. `<job>/analysis/shotgun-gutsmash/`:

```bash
export GUTSMASH_DB=<resolved gutsmash_db.path>
python run_gutsmash.py \
  --sequence <job>/stage/genome.fna \
  --output-dir <job>/analysis/shotgun-gutsmash \
  --threads 8
```

FASTA without CDS needs `--genefinding-tool prodigal` (the helper default).
Do not invent cluster tables if the DB or tool is missing.

## Agent procedure

1. Stage GenBank / EMBL / FASTA under `stage/`.
2. Resolve `gutsmash_db` from `registry/references.yaml` (ask if missing).
3. Copy/adapt `scripts/run_gutsmash.py` into the job (or
   `conda run -n gutsmash --no-capture-output gutsmash --databases …`).
4. Write under `analysis/shotgun-gutsmash/`.

## Ask the user when unknown

- Extra modules (`--cb-general`, `--cb-knownclusters`, `--fullhmmer`, `--clusterhmmer`)
- Already-annotated GBK vs FASTA (gene finding)
