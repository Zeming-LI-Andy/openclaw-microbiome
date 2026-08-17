---
name: shotgun-gapseq
description: >
  Predict bacterial pathways and reconstruct genome-scale models with gapseq.
runtime: gapseq
conda_env: gapseq
tools:
  - gapseq
  - python
---

# Metabolic reconstruction (gapseq)

## Runtime

| Field | Value |
|-------|-------|
| Runtime id | `gapseq` |
| Conda env | `gapseq` |

DB: look up `gapseq_sequences` in `registry/references.yaml`. If missing, ask
the user — do not invent. That path is the **seq root** (`Bacteria/` /
`Archaea/` with UniProt archives). Pass it as `-D`. Pathway tables, media, and
biomass live in the conda env `dat/` — do not replace those from the ref tree.

Never run `gapseq update-sequences`. Always pass `-O` on `find` / `doall` so a
missing archive cannot fetch UniProt/Zenodo.

Bootstrap may symlink `dat/seq/Bacteria` and `Archaea`; still pass `-D` from
the resolved path.

## Reference script (`scripts/`)

Reference (path relative to this skill): `scripts/run_gapseq.py`
(`find`, `find-transport`, `doall`).

**Copy/adapt** it under the session job; do not run against the skill tree as
cwd. Run **one subcommand per step**. After copying to e.g.
`<job>/analysis/shotgun-gapseq/`:

```bash
export GAPSEQ_SEQ_DIR=<resolved gapseq_sequences.path>
python run_gapseq.py find \
  --genome <job>/stage/genome.faa \
  --output-dir <job>/analysis/shotgun-gapseq/find \
  --threads 8

python run_gapseq.py find-transport \
  --genome <job>/stage/genome.faa \
  --output-dir <job>/analysis/shotgun-gapseq/find-transport \
  --threads 8

# Combined reconstruction (long). Prefer split find → draft → fill if iterating.
python run_gapseq.py doall \
  --genome <job>/stage/genome.faa \
  --output-dir <job>/analysis/shotgun-gapseq/doall \
  --threads 8
```

`draft` / `medium` / `fill` / `adapt` are not wrapped — call
`conda run -n gapseq --no-capture-output gapseq …` with this job’s tables.

Do not invent models if sequences or gapseq are missing.

## Agent procedure

1. Stage nucleotide or protein FASTA under `stage/`.
2. Resolve `gapseq_sequences` from `registry/references.yaml` (ask if missing).
3. Copy/adapt `scripts/run_gapseq.py` into the job.
4. Write under `analysis/shotgun-gapseq/` (one subdirectory per subcommand).

## Ask the user when unknown

- `find` only vs `doall` (full GEM)
- Taxonomic range (`-t` Bacteria / Archaea / auto)
- Pathway keyword (`-p all` vs a subsystem)
- Aligner (`-A` blast / diamond / mmseqs2)
