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

`scripts/annotate_vfdb.py` — **reference only**. Adapt paths/flags to the job.

```bash
export VFDB_DMND=<resolved>
python skills/shotgun-vfdb/scripts/annotate_vfdb.py \
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
3. Adapt the reference script or run equivalent `emapper.py --no_annot --dmnd_db …`.
4. Write under `analysis/shotgun-vfdb/`.

## Ask the user when unknown

- Protein vs contig input (ORF call first if contigs)
- Threads / which DB build is available
