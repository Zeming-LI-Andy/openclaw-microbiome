---
name: sra-search
description: >
  Search NCBI SRA for public sequencing datasets (metadata only: accessions,
  organism, platform, BioProject/BioSample). Does not download FASTQ.
runtime: host
conda_env: mcp_server
tools:
  - python
---

# NCBI SRA metadata search

## Purpose

Find public SRA runs/experiments before staging local data. **Metadata only** —
no `prefetch` / `fasterq-dump` unless the user explicitly asks for download
(handle that as a separate step with appropriate tools and quota).

## Reference script (`scripts/`)

`scripts/search_sra.py` — Entrez `esearch` + `esummary` via stdlib. Reference
only; adjust `retmax`, filters, and output paths.

```bash
python skills/sra-search/scripts/search_sra.py \
  --query "gut microbiome IBD 16S" \
  --organism "Homo sapiens" \
  --retmax 10 \
  --json-out <job>/analysis/sra-search/hits.json
```

Optional env: `NCBI_API_KEY`, `NCBI_EMAIL` (higher rate limits).

## Agent procedure

1. Clarify search intent (disease, organism, strategy, known SRR/ERR/DRR).
2. Run the reference script (or equivalent E-utilities calls).
3. Save human-readable summary + JSON under `analysis/sra-search/`.
4. If the user picks accessions for analysis, stage/download in a **later** step
   — do not invent FASTQ contents.

## Useful filters

- Organism: `--organism "Homo sapiens"`
- Strategy: `--library-strategy AMPLICON` / `WGS` / `RNA-Seq`
- Direct accession: `--query SRR390728`
