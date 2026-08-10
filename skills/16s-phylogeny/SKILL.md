---
name: 16s-phylogeny
description: >
  Build a rooted phylogeny from representative sequences (MAFFT + FastTree via QIIME 2).
runtime: qiime2-amplicon
conda_env: qiime2-amplicon-2024.10
docker_image: openclaw/amplicon:1.0.0
tools:
  - qiime
---

# 16S phylogeny

## Runtime

| Field | Value |
|-------|-------|
| Runtime id | `qiime2-amplicon` |
| Conda env | `qiime2-amplicon-2024.10` |
| Docker image | `openclaw/amplicon:1.0.0` |

## Available tools

- `qiime` — e.g. `qiime phylogeny align-to-tree-mafft-fasttree`

## Agent procedure

1. Input: representative sequences `.qza`.
2. Read `--help`, then run via Bash in the skill conda/Docker runtime.
3. Write alignment/tree artifacts under `analysis/16s-phylogeny/`.
