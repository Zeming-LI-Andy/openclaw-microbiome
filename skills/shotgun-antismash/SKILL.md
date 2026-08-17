---
name: shotgun-antismash
description: >
  Detect secondary metabolite biosynthetic gene clusters with official antiSMASH 8.
runtime: antismash
conda_env: antismash
tools:
  - antismash
  - python
---

# Secondary metabolite BGCs (antiSMASH)

## Runtime

| Field | Value |
|-------|-------|
| Runtime id | `antismash` |
| Conda env | `antismash` |

DB: look up `antismash_db` in `registry/references.yaml`. If missing, ask the
user — do not invent. Pass that directory as `--databases`.

Never run `download-antismash-databases`. Bootstrap may symlink the default
`antismash/databases` directory; still pass `--databases` from the resolved
path.

## Reference script (`scripts/`)

Reference (path relative to this skill): `scripts/run_antismash.py`.

**Copy/adapt** it under the session job; do not run against the skill tree as
cwd. After copying to e.g. `<job>/analysis/shotgun-antismash/`:

```bash
export ANTISMASH_DB=<resolved antismash_db.path>
python run_antismash.py \
  --sequence <job>/stage/genome.gbk \
  --output-dir <job>/analysis/shotgun-antismash \
  --threads 8
```

FASTA without CDS: add `--genefinding-tool prodigal` (helper default for
non-GenBank suffixes). Do not invent cluster HTML/JSON if the DB or tool is
missing.

## Agent procedure

1. Stage GenBank / FASTA under `stage/`.
2. Resolve `antismash_db` from `registry/references.yaml` (ask if missing).
3. Copy/adapt `scripts/run_antismash.py` into the job (or
   `conda run -n antismash --no-capture-output antismash --databases …`).
4. Write under `analysis/shotgun-antismash/`.

## Ask the user when unknown

- Taxon (`--taxon` bacteria vs fungi)
- Extra analyses (`--cb-knownclusters`, `--cc-mibig`, `--fullhmmer`, `--tigrfam`)
- Already-annotated GBK vs FASTA (gene finding)
