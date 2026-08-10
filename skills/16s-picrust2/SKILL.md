---
name: 16s-picrust2
description: >
  Predict metagenome functions from 16S ASV sequences and abundance tables with PICRUSt2.
runtime: picrust2
conda_env: picrust2
docker_image: openclaw/amplicon:1.0.0
docker_conda_env: picrust2
tools:
  - picrust2_pipeline.py
  - place_seqs.py
  - hsp.py
  - metagenome_pipeline.py
  - pathway_pipeline.py
  - add_descriptions.py
---

# 16S functional prediction (PICRUSt2)

## Runtime

| Field | Value |
|-------|-------|
| Runtime id | `picrust2` |
| Conda env | `picrust2` |
| Docker image | `openclaw/amplicon:1.0.0` (nested `conda run -n picrust2` when using Docker) |

## Available tools

- `picrust2_pipeline.py` — full pipeline entry
- Intermediate helpers: `place_seqs.py`, `hsp.py`, `metagenome_pipeline.py`, `pathway_pipeline.py`, `add_descriptions.py`

Prefer `conda run -n picrust2 picrust2_pipeline.py --help`.

## Inputs

Usually exported ASV FASTA + abundance TSV (from `16s-export` or equivalent). Stage or point to paths under the job.

## Agent procedure

1. Confirm sequences + table exist.
2. Build argv from `--help`; output under `analysis/16s-picrust2/`.
3. Run under conda env `picrust2` (or the amplicon image nested env).

## Ask the user when unknown

- Stratified output, which pathway/EC tables they need
