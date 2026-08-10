---
name: shotgun-eggnog
description: >
  Annotate genes / proteins with EggNOG-mapper (and Prodigal for ORF calling when needed).
runtime: eggnog_mapper
conda_env: eggnog_mapper
tools:
  - eggnog-mapper
  - emapper.py
  - prodigal
  - python
---

# Shotgun functional annotation (EggNOG-mapper)

## Runtime

| Field | Value |
|-------|-------|
| Runtime id | `eggnog_mapper` |
| Conda env | `eggnog_mapper` |

DB: look up paths in `registry/references.yaml`. If missing, ask the user —
do not invent.

## Reference script (`scripts/`)

`scripts/annotate_eggnog.py` — **reference only**. Copy/adapt under the session
job; pass DB paths via flags or env after resolving them from
`registry/references.yaml`.

```bash
export EGGNOG_DATA_DIR=<resolved>
export EGGNOG_DMND=<resolved>
python skills/shotgun-eggnog/scripts/annotate_eggnog.py \
  --protein <job>/stage/proteins.faa \
  --output-dir <job>/analysis/shotgun-eggnog \
  --threads 8
```

For virulence factor screening use `shotgun-vfdb`; for AMR use `shotgun-rgi`.
Do not invent annotation tables if the DB or tool is missing.

## Agent procedure

1. `mgx_create_job`; stage proteins or contigs under `stage/`.
2. If starting from contigs, run Prodigal first into `analysis/shotgun-eggnog/`.
3. Resolve DBs from `registry/references.yaml` (ask if missing); adapt the
   reference script or equivalent `conda run … emapper.py`.
4. Write under `analysis/shotgun-eggnog/`.

## Ask the user when unknown

- Input type (protein FASTA vs contigs)
- Taxonomic scope / which Diamond DB
- CPU threads
