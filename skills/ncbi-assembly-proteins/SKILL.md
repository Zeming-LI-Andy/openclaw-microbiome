---
name: ncbi-assembly-proteins
description: >
  Download NCBI Assembly protein FASTA (*_protein.faa) by organism name for
  downstream annotation (EggNOG / VFDB / RGI, etc.).
runtime: host
conda_env: mgx-base
tools:
  - python
---

# NCBI Assembly protein fetch

## Purpose

Pull public Assembly protein sets when the user names an organism but has no
local `.faa`. Metadata/download only — not functional annotation (use
`shotgun-eggnog`, `shotgun-vfdb`, `shotgun-rgi` afterwards).

## Reference script (`scripts/`)

Reference (path relative to this skill): `scripts/fetch_ncbi_assembly_proteins.py`.

**Copy/adapt** it under the session job; do not run against the skill tree as
cwd. After copying to e.g. `<job>/stage/` or
`<job>/analysis/ncbi-assembly-proteins/`:

```bash
python fetch_ncbi_assembly_proteins.py \
  --organism "Escherichia coli K-12" \
  --output-dir <job>/stage
```

Optional: set `NCBI_API_KEY` / `NCBI_EMAIL` for higher Entrez limits.

## Agent procedure

1. Confirm organism string (and whether RefSeq is required).
2. Copy/adapt `scripts/fetch_ncbi_assembly_proteins.py` into the job; stage
   `.faa` under `stage/` or `analysis/ncbi-assembly-proteins/`.
3. Hand off to the appropriate annotation skill — do not invent sequences.
