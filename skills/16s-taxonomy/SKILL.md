---
name: 16s-taxonomy
description: >
  Assign taxonomy to representative sequences with a pretrained QIIME 2 classifier.
runtime: qiime2-amplicon
conda_env: qiime2-amplicon-2024.10
docker_image: openclaw/amplicon:1.0.0
tools:
  - qiime
---

# 16S taxonomy assignment

## Runtime

| Field | Value |
|-------|-------|
| Runtime id | `qiime2-amplicon` |
| Conda env | `qiime2-amplicon-2024.10` |

Classifiers / reference DBs: look up paths in `registry/references.yaml`. If a
needed path is missing, do not invent — ask the user.

## Available tools

- `qiime` — commonly `qiime feature-classifier classify-sklearn` (or other classifiers present in the env)

## Agent procedure

1. Confirm rep-seqs `.qza` and classifier `.qza` paths (from
   `registry/references.yaml` or the user).
2. If classifier path unknown, ask the user (do not invent).
3. Run via Bash with args from `--help`; outputs under `analysis/16s-taxonomy/`.
