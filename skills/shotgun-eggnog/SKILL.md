---
name: shotgun-eggnog
description: >
  Annotate proteins with EggNOG-mapper.
runtime: eggnog_mapper
conda_env: eggnog_mapper
tools:
  - eggnog-mapper
  - emapper.py
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

Reference (path relative to this skill): `scripts/annotate_eggnog.py`.

**Copy/adapt** it under the session job; pass DB paths via flags or env after
resolving them from `registry/references.yaml`. Do not run against the skill
tree as cwd. After copying to e.g. `<job>/analysis/shotgun-eggnog/`:

```bash
export EGGNOG_DATA_DIR=<resolved>
export EGGNOG_DMND=<resolved>
python annotate_eggnog.py \
  --protein <job>/stage/proteins.faa \
  --output-dir <job>/analysis/shotgun-eggnog \
  --threads 8
```

For virulence factor screening use `shotgun-vfdb`; for AMR use `shotgun-rgi`.
Do not invent annotation tables if the DB or tool is missing.

## Agent procedure

1. Stage protein FASTA under the session `stage/`.
2. Resolve DBs from `registry/references.yaml` (ask if missing); copy/adapt
   `scripts/annotate_eggnog.py` into the job (or equivalent
   `conda run … emapper.py`).
3. Write under `analysis/shotgun-eggnog/`.

## Ask the user when unknown

- Taxonomic scope / which Diamond DB
