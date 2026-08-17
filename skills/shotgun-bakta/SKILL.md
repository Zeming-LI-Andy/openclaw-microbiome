---
name: shotgun-bakta
description: >
  Annotate bacterial genomes, MAGs, or plasmids with Bakta (nucleotide FASTA).
runtime: bakta
conda_env: bakta
tools:
  - bakta
  - bakta_proteins
  - python
---

# Bacterial genome annotation (Bakta)

## Runtime

| Field | Value |
|-------|-------|
| Runtime id | `bakta` |
| Conda env | `bakta` |

DB: look up `bakta_db` in `registry/references.yaml`. If missing, ask the user —
do not invent. The path must be the directory that contains `version.json`
(schema major 6 for Bakta 1.12.x), not a parent download folder.

Never run `bakta_db download` / `bakta_db update` / `amrfinder_update` during
analysis. Bootstrap may already export `BAKTA_DB`; still pass `--db` from the
resolved path.

## Reference script (`scripts/`)

Reference (path relative to this skill): `scripts/annotate_bakta.py`.

**Copy/adapt** it under the session job; do not run against the skill tree as
cwd. After copying to e.g. `<job>/analysis/shotgun-bakta/`:

```bash
export BAKTA_DB=<resolved bakta_db.path>
python annotate_bakta.py \
  --genome <job>/stage/genome.fna \
  --output-dir <job>/analysis/shotgun-bakta \
  --threads 8
```

Protein-only (no contig annotation): `--mode proteins --protein <job>/stage/proteins.faa`.

Do not invent GFF/GBFF if Bakta or the DB is missing.

## Agent procedure

1. Stage nucleotide FASTA (or protein FASTA for `bakta_proteins`) under `stage/`.
2. Resolve `bakta_db` from `registry/references.yaml` (ask if missing).
3. Copy/adapt `scripts/annotate_bakta.py` into the job (or
   `conda run -n bakta --no-capture-output bakta --db …`).
4. Write under `analysis/shotgun-bakta/`.

## Ask the user when unknown

- Complete replicons vs MAG (`--complete` / `--meta`)
- Genus / species / strain labels
- Translation table (11 / 4 / 25)
