---
name: 16s-diversity
description: >
  Run core alpha/beta diversity metrics on a feature table with phylogeny and metadata.
runtime: qiime2-amplicon
conda_env: qiime2-amplicon-2024.10
docker_image: openclaw/amplicon:1.0.0
tools:
  - qiime
---

# 16S diversity

## Runtime

| Field | Value |
|-------|-------|
| Runtime id | `qiime2-amplicon` |
| Conda env | `qiime2-amplicon-2024.10` |
| Docker image | `openclaw/amplicon:1.0.0` |

## Available tools

- `qiime` — e.g. `qiime diversity core-metrics-phylogenetic` and follow-up group-significance / emperor plugins as needed

## Agent procedure

1. Need table, rooted tree, metadata, and a **sampling depth** (from summarize + user).
2. Ask for sampling depth if unknown — never invent a silent default for publication work.
3. Build commands from `--help`; write under `analysis/16s-diversity/`.
