---
name: 16s-feature-summarize
description: >
  Summarize a QIIME 2 feature table (sample depths, sparseness) before choosing
  rarefaction / sampling depth.
runtime: qiime2-amplicon
conda_env: qiime2-amplicon-2024.10
docker_image: openclaw/amplicon:1.0.0
tools:
  - qiime
---

# 16S feature table summarize

## Runtime

| Field | Value |
|-------|-------|
| Runtime id | `qiime2-amplicon` |
| Conda env | `qiime2-amplicon-2024.10` |
| Docker image | `openclaw/amplicon:1.0.0` |

## Available tools

- `qiime` — typically `qiime feature-table summarize`

## Agent procedure

1. Point at table `.qza` from denoise (or upstream).
2. Optionally attach `stage/metadata.tsv` if present.
3. Build argv from `--help`; write `.qzv` under `analysis/16s-feature-summarize/` via Bash in the skill conda env.
4. Use the summary with the user to pick sampling depth for diversity later.
