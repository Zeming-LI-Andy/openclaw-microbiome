---
name: shotgun-aviary
description: >
  Run Aviary metagenome assembly / binning / recovery workflows when the user
  wants MAG-oriented analysis.
runtime: aviary
conda_env: aviary
tools:
  - aviary
---

# Shotgun assembly / binning (Aviary)

## Runtime

| Field | Value |
|-------|-------|
| Runtime id | `aviary` |
| Conda env | `aviary` |

Reference DBs: look up paths in `registry/references.yaml`. If missing, ask
the user — do not invent. Export env vars / flags for the run from those paths.
Do not hardcode host-specific absolute paths into commands you reuse across
machines.

## Reference script (`scripts/`)

`scripts/aviary_assemble_recover.py` is a **reference** wrapper for
`aviary assemble` and `aviary recover`. Copy/adapt it; pass reads, output dir,
and DB paths via CLI/env. Cluster/dereplicate is not covered — call Aviary
directly if needed.

```bash
# After resolving DBs into env vars:
python skills/shotgun-aviary/scripts/aviary_assemble_recover.py assemble \
  --output-dir <job>/analysis/shotgun-aviary/assemble \
  -1 <job>/stage/R1.fq.gz -2 <job>/stage/R2.fq.gz

python skills/shotgun-aviary/scripts/aviary_assemble_recover.py recover \
  --output-dir <job>/analysis/shotgun-aviary/recover \
  --assembly <job>/analysis/shotgun-aviary/assemble/assembly/final_contigs.fasta \
  -1 <job>/stage/R1.fq.gz -2 <job>/stage/R2.fq.gz \
  --gtdb-path "$GTDBTK_DATA_PATH" \
  --checkm2-db-path "$CHECKM2DB" \
  --singlem-metapackage-path "$SINGLEM_METAPACKAGE_PATH" \
  --eggnog-db-path "$EGGNOG_DATA_DIR"
```

Run **assemble** and **recover** as separate steps (see `CODING.md`).

## Agent procedure

1. `mgx_create_job` + stage reads.
2. Resolve DBs from `registry/references.yaml` (ask if missing); set env or flags.
3. Adapt the reference script or build equivalent `conda run -n aviary aviary …`.
4. Write under `analysis/shotgun-aviary/`.

## Ask the user when unknown

- Assembly vs recover vs both
- Threads / memory
- Which reference packs are available on this host
