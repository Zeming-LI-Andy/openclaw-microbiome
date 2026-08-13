---
name: stats-differential-abundance
description: >
  Differential abundance / association testing on feature tables (e.g. MaAsLin3,
  DESeq2) using the stats conda env.
runtime: stats
conda_env: mgx-base
tools:
  - R
  - Rscript
  - python
  - maaslin3
  - DESeq2
  - pandas
---

# Differential abundance / associations

## Runtime

| Field | Value |
|-------|-------|
| Runtime id | `stats` |
| Conda env | `mgx-base` |

See `registry/runtimes.yaml` → `stats` for available R/Python packages.

## Inputs

Typically a feature table + sample metadata under the session job
(`stage/` or exported from QIIME / MetaPhlAn / HUMAnN).

## Agent procedure

1. Confirm table + metadata columns with the user (phenotype, covariates).
2. Choose method (MaAsLin3, DESeq2, …) appropriate to the design.
3. Run via `conda run -n mgx-base Rscript …` or Python; write
   `analysis/stats-differential-abundance/`.
4. Summarize significant features clearly; do not overclaim causality.

## Ask the user when unknown

- Outcome / grouping variable
- Covariates, multiple-testing policy
- Preferred tool (MaAsLin3 vs DESeq2 vs other)
