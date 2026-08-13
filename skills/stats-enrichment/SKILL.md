---
name: stats-enrichment
description: >
  Pathway / KO enrichment and related gene-set analyses (clusterProfiler,
  gseapy, local KEGG maps).
runtime: stats
conda_env: mgx-base
tools:
  - R
  - Rscript
  - python
  - clusterProfiler
  - KEGGREST
  - gseapy
---

# Functional enrichment

## Runtime

| Field      | Value        |
| ------------| --------------|
| Runtime id | `stats`      |
| Conda env  | `mgx-base` |

Local mapping tables: look up paths in `registry/references.yaml`. If missing,
ask the user — do not invent.

## Agent procedure

1. Obtain gene/KO/feature hit lists from upstream annotation (PICRUSt2, HUMAnN, EggNOG, …).
2. If using local mapping, resolve paths from `registry/references.yaml` (ask if missing).
3. Run enrichment in `mgx-base`; write `analysis/stats-enrichment/`.

Also see skill `annotation-kegg` for KEGG REST / ID lookup guidance.
