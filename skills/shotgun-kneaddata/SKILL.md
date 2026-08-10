---
name: shotgun-kneaddata
description: >
  Quality-trim and optionally decontaminate shotgun metagenomic reads with KneadData.
runtime: biobakery
conda_env: biobakery_workflows
docker_image: null
tools:
  - kneaddata
  - bowtie2
---

# Shotgun QC / decontamination (KneadData)

## Runtime

| Field        | Value                       |
| --------------| -----------------------------|
| Runtime id   | `biobakery`                 |
| Conda env    | `biobakery_workflows`       |
| Docker image | _(none pinned — use conda)_ |

## Available tools

- `kneaddata`
- `bowtie2` (used internally / for host DB)

## Agent procedure

1. Stage FASTQs under `stage/`.
2. When decontamination needs a host/reference DB, look up the path in
   `registry/references.yaml`. If missing, ask the user — do not invent.
3. `conda run -n biobakery_workflows kneaddata --help` then build argv; outputs under `analysis/shotgun-kneaddata/`.
