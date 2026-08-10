---
name: shotgun-humann
description: >
  Profile microbial pathways and gene families from shotgun reads with HUMAnN.
runtime: biobakery
conda_env: biobakery_workflows
docker_image: null
tools:
  - humann
  - humann3
  - metaphlan
---

# Shotgun functional profiling (HUMAnN)

## Runtime

| Field | Value |
|-------|-------|
| Runtime id | `biobakery` |
| Conda env | `biobakery_workflows` |
| Docker image | _(none pinned — use conda)_ |

## Available tools

- `humann` and/or `humann3` (whichever is on PATH in the env — check with `--help`)
- `metaphlan` (HUMAnN may call it unless a taxonomic profile is supplied)

## Agent procedure

1. Choose binary present in the env (`humann` vs `humann3`).
2. Look up required DB paths in `registry/references.yaml`. If missing, ask the
   user — do not invent.
3. Optionally pass an existing MetaPhlAn profile.
4. Build and run via Bash; outputs under `analysis/shotgun-humann/`.
