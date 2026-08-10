---
name: shotgun-aviary
description: >
  Run Aviary metagenome assemble / recover / annotate / cluster workflows when
  the user wants MAG-oriented analysis.
runtime: aviary
conda_env: aviary
tools:
  - aviary
---

# Shotgun assembly / MAG recovery (Aviary)

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

Reference (path relative to this skill): `scripts/aviary_assemble_recover.py`
(wraps `aviary assemble` / `recover` / `annotate` / `cluster`).

**Copy/adapt** it into the session job; do not run against the skill tree as
cwd. `complete` / `configure` / `build` / `isolate` are not wrapped — call
Aviary directly if needed.

After copying to e.g. `<job>/analysis/shotgun-aviary/`:

```bash
# After resolving DBs into env vars:
python aviary_assemble_recover.py assemble \
  --output-dir <job>/analysis/shotgun-aviary/assemble \
  -1 <job>/stage/R1.fq.gz -2 <job>/stage/R2.fq.gz

# Optional: MEGAHIT short-read assembly
python aviary_assemble_recover.py assemble \
  --output-dir <job>/analysis/shotgun-aviary/assemble \
  -1 <job>/stage/R1.fq.gz -2 <job>/stage/R2.fq.gz \
  --use-megahit

# Optional: hybrid (short + long; default long assembler myloasm)
python aviary_assemble_recover.py assemble \
  --output-dir <job>/analysis/shotgun-aviary/assemble \
  -1 <job>/stage/R1.fq.gz -2 <job>/stage/R2.fq.gz \
  --long-reads <job>/stage/long.fq.gz --long-read-type ont

python aviary_assemble_recover.py recover \
  --output-dir <job>/analysis/shotgun-aviary/recover \
  --assembly <job>/analysis/shotgun-aviary/assemble/assembly/final_contigs.fasta \
  -1 <job>/stage/R1.fq.gz -2 <job>/stage/R2.fq.gz \
  --gtdb-path "$GTDBTK_DATA_PATH" \
  --checkm2-db-path "$CHECKM2DB" \
  --singlem-metapackage-path "$SINGLEM_METAPACKAGE_PATH" \
  --eggnog-db-path "$EGGNOG_DATA_DIR"

# Binning only (skip recover post-binning taxonomy/annotation):
#   … recover … --binning-only

python aviary_assemble_recover.py annotate \
  --output-dir <job>/analysis/shotgun-aviary/annotate \
  --genome-fasta-directory <job>/analysis/shotgun-aviary/recover/bins/final_bins \
  --gtdb-path "$GTDBTK_DATA_PATH" \
  --eggnog-db-path "$EGGNOG_DATA_DIR" \
  --checkm2-db-path "$CHECKM2DB"

# After multiple recover (or complete) runs — Galah dereplication:
python aviary_assemble_recover.py cluster \
  --output-dir <job>/analysis/shotgun-aviary/cluster \
  --input-runs <job>/analysis/shotgun-aviary/recover <other>/recover
```

Run **assemble**, **recover**, **annotate**, and **cluster** as separate steps
(see `CODING.md`). Default `recover` is **full** MAG recovery; pass
`--binning-only` only when you want bins without recover’s post-binning steps.
Protein-only EggNOG (non-MAG): use `shotgun-eggnog`.

## Agent procedure

1. Stage reads (and long reads if hybrid) under the session job.
2. Resolve DBs from `registry/references.yaml` (ask if missing); set env or flags.
3. Copy/adapt `scripts/aviary_assemble_recover.py` into the job (or equivalent
   `conda run -n aviary aviary …`).
4. Write under `analysis/shotgun-aviary/`.

## Ask the user when unknown

- Which stages: assemble / recover / annotate / cluster (or combination)
- Short-only vs hybrid / long-only; MEGAHIT vs default short assembler
- Full recover vs `--binning-only`
- Memory limits if relevant
- Which reference packs are available on this host
- For `cluster`: which prior recover output dirs; ANI threshold if non-default
