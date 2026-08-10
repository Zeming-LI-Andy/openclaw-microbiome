---
name: 16s-export
description: >
  Export QIIME 2 artifacts (.qza/.qzv) to flat files (BIOM, FASTA, TSV, etc.).
runtime: qiime2-amplicon
conda_env: qiime2-amplicon-2024.10
docker_image: openclaw/amplicon:1.0.0
tools:
  - qiime
  - biom
---

# 16S export

## Runtime

| Field | Value |
|-------|-------|
| Runtime id | `qiime2-amplicon` |
| Conda env | `qiime2-amplicon-2024.10` |
| Docker image | `openclaw/amplicon:1.0.0` |

## Available tools

- `qiime` — `qiime tools export`
- `biom` — convert BIOM ↔ TSV when needed

## Agent procedure

1. Choose artifact path and export directory under `analysis/16s-export/`.
2. Construct `qiime tools export …` (and optional `biom` commands) via Bash in the skill runtime.
