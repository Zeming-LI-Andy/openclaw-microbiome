---
name: ncbi-assembly-proteins
description: >
  Download NCBI Assembly protein FASTA (*_protein.faa) by organism name for
  downstream annotation (EggNOG / VFDB / RGI, etc.).
runtime: host
conda_env: mcp_server
tools:
  - python
---

# NCBI Assembly protein fetch

## Purpose

Pull public Assembly protein sets when the user names an organism but has no
local `.faa`. Metadata/download only — not functional annotation (use
`shotgun-eggnog`, `shotgun-vfdb`, `shotgun-rgi` afterwards).

## Reference script (`scripts/`)

`scripts/fetch_ncbi_assembly_proteins.py` — **reference only**. Adjust filters
(RefSeq vs GenBank), rate limits, and output layout for the session job.

```bash
python skills/ncbi-assembly-proteins/scripts/fetch_ncbi_assembly_proteins.py \
  --organism "Escherichia coli K-12" \
  --output-dir <job>/stage
```

Optional: set `NCBI_API_KEY` / `NCBI_EMAIL` for higher Entrez limits.

## Agent procedure

1. `mgx_create_job` if needed.
2. Confirm organism string (and whether RefSeq is required).
3. Adapt the reference script; stage `.faa` under `stage/` or
   `analysis/ncbi-assembly-proteins/`.
4. Hand off to the appropriate annotation skill — do not invent sequences.
