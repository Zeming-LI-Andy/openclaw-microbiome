---
name: 16s-denoise-dada2
description: >
  Denoise paired-end (or single-end) amplicon reads with QIIME 2 DADA2.
  Use after a demux .qza exists.
runtime: qiime2-amplicon
conda_env: qiime2-amplicon-2024.10
docker_image: openclaw/amplicon:1.0.0
tools:
  - qiime
---

# 16S denoise (DADA2)

## Goal

Produce feature table + representative sequences from demultiplexed reads.

## Runtime

| Field | Value |
|-------|-------|
| Runtime id | `qiime2-amplicon` |
| Conda env | `qiime2-amplicon-2024.10` |
| Docker image | `openclaw/amplicon:1.0.0` |

## Available tools

- `qiime` — `qiime dada2 denoise-paired` / `denoise-single` / related plugins

Inspect with `conda run -n qiime2-amplicon-2024.10 qiime dada2 denoise-paired --help`.

## Job layout

- Input: demux `.qza` (often from `analysis/16s-import/`)
- Output: `analysis/16s-denoise-dada2/` (table, rep-seqs, stats)

## Agent procedure

1. Confirm demux artifact exists under this session job.
2. Ask user for truncation lengths if unknown (`trunc-len-f` / `trunc-len-r`).
3. Run `qiime dada2 …` via Bash in the conda env above; keep outputs in `analysis/16s-denoise-dada2/`.

## Ask the user when unknown

- Truncation / trim lengths
- Paired vs single-end plugin
