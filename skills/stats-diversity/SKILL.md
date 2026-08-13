---
name: stats-diversity
description: >
  Downstream alpha/beta diversity and ordination on non-QIIME tables (or on
  exported QIIME artifacts) with scikit-bio / vegan-style workflows in the
  stats env.
runtime: stats
conda_env: mgx-base
tools:
  - python
  - R
  - Rscript
  - scikit-bio
  - pandas
  - matplotlib
  - ggplot2
---

# Downstream diversity (stats env)

Use this when diversity should be computed outside QIIME core-metrics, or on
shotgun profiles (MetaPhlAn / HUMAnN).

## Runtime

| Field | Value |
|-------|-------|
| Runtime id | `stats` |
| Conda env | `mgx-base` |

For QIIME-native core metrics, prefer skill `16s-diversity` instead.

## Agent procedure

1. Locate abundance table + metadata in the session job.
2. Choose metrics (Shannon, Bray–Curtis, UniFrac only if tree available, etc.).
3. Run Python/R in `mgx-base`; figures/tables under `analysis/stats-diversity/`.
