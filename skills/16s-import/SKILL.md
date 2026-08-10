---
name: 16s-import
description: >
  Import demultiplexed 16S / amplicon reads into a QIIME 2 artifact.
  Use when starting an amplicon analysis from FASTQ + manifest.
runtime: qiime2-amplicon
conda_env: qiime2-amplicon-2024.10
docker_image: openclaw/amplicon:1.0.0
tools:
  - qiime
  - biom
---

# 16S import (QIIME 2)

## Goal

Turn staged FASTQ + manifest into a QIIME 2 `.qza` (typically demultiplexed sequences).

## Runtime

| Field | Value |
|-------|-------|
| Runtime id | `qiime2-amplicon` |
| Conda env | `qiime2-amplicon-2024.10` |
| Docker image | `openclaw/amplicon:1.0.0` |

Run under this session's job dir with Bash, e.g.
`conda run -n qiime2-amplicon-2024.10 --no-capture-output qiime tools import …`

## Available tools in this environment

- `qiime` — primary CLI (`qiime tools import`, `qiime tools peek`, …)
- `biom` — optional table conversion later

Discover flags with `conda run -n qiime2-amplicon-2024.10 qiime tools import --help`.

## Job layout

- Inputs under `stage/` (e.g. `manifest.tsv`, FASTQ paths listed in the manifest)
- Outputs under `analysis/16s-import/` (create as needed)

## Agent procedure

1. Stage manifest + reads into this session job.
2. Read this skill for runtime + tool names.
3. If unsure of type/format, run `--help` in the conda env above.
4. Run import with paths under this job, e.g.:

   `qiime tools import --type … --input-path <stage/manifest> --input-format … --output-path <analysis/16s-import/demux.qza>`

## Ask the user when unknown

- Semantic type and input format (paired vs single, manifest version)
- Absolute vs relative FASTQ paths inside the manifest
