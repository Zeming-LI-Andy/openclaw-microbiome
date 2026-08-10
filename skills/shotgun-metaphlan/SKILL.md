---
name: shotgun-metaphlan
description: >
  Profile microbial composition from shotgun reads with MetaPhlAn.
runtime: biobakery
conda_env: biobakery_workflows
docker_image: null
tools:
  - metaphlan
  - bowtie2
---

# Shotgun taxonomic profiling (MetaPhlAn)

## Runtime

| Field | Value |
|-------|-------|
| Runtime id | `biobakery` |
| Conda env | `biobakery_workflows` |
| Docker image | _(none pinned — use conda)_ |

## Available tools

- `metaphlan`
- `bowtie2`

## Agent procedure

1. Prefer KneadData-cleaned reads when available.
2. If a MetaPhlAn DB path is required, look it up in `registry/references.yaml`.
   If missing, ask the user — do not invent.
3. Inspect `metaphlan --help` in `biobakery_workflows`; construct argv.
4. Write profile (+ optional bowtie2out) under `analysis/shotgun-metaphlan/`.
