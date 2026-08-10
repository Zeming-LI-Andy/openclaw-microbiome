---
name: shotgun-vfdb
description: >
  Screen proteins against VFDB with EggNOG-mapper Diamond (--no_annot).
runtime: eggnog_mapper
conda_env: eggnog_mapper
tools:
  - emapper.py
  - eggnog-mapper
  - python
---

# Virulence factors (VFDB via emapper)

## Runtime

| Field | Value |
|-------|-------|
| Runtime id | `eggnog_mapper` |
| Conda env | `eggnog_mapper` (same stack as EggNOG-mapper) |

DB: look up paths in `registry/references.yaml`. If missing, ask the user —
do not invent.

## Reference script (`scripts/`)

Reference (path relative to this skill): `scripts/annotate_vfdb.py`.

**Copy/adapt** it under the session job; do not run against the skill tree as
cwd. After copying to e.g. `<job>/analysis/shotgun-vfdb/`:

```bash
export VFDB_DMND=<resolved>
python annotate_vfdb.py \
  --protein <job>/stage/proteins.faa \
  --output-dir <job>/analysis/shotgun-vfdb \
  --threads 8
```

Primary output is typically `*.emapper.seed_orthologs` (Diamond hits; no full
EggNOG annotation). Do not fabricate virulence calls if the DB is missing.

## Agent procedure

1. Stage protein FASTA under the session job.
2. Resolve the DB path from `registry/references.yaml` (ask if missing); set
   `VFDB_DMND` or `--vfdb-dmnd`.
3. Copy/adapt `scripts/annotate_vfdb.py` into the job (or equivalent
   `emapper.py --no_annot --dmnd_db …`).
4. Write under `analysis/shotgun-vfdb/`.

## Ask the user when unknown

- Protein vs contig input (ORF call first if contigs)
- Which DB build is available
