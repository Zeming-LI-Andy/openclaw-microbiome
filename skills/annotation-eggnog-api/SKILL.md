---
name: annotation-eggnog-api
description: >
  Query EggNOG orthologous groups via the EggNOG REST URL API (trees, alignments,
  domains, GO). Distinct from local eggnog-mapper runs (see `shotgun-eggnog`).
runtime: host
conda_env: mgx-base
tools:
  - python
  - curl
---

# EggNOG REST API

## URL pattern

```text
http://eggnogapi5.embl.de/nog_data/[dataformat]/[attributes]/[nogname]
```

- `dataformat`: `json` | `text` | `file` | `html`
- `attributes`: e.g. `fasta`, `raw_alg`, `trimmed_alg`, `tree`, `go_terms`, `domains`
  (comma-separated for `json`/`file`)
- `nogname`: e.g. `ENOG502QVY3` or `COG0575`

Examples:

```bash
curl -sL "http://eggnogapi5.embl.de/nog_data/json/tree/ENOG502QVY3"
curl -sL "http://eggnogapi5.embl.de/nog_data/json/domains/ENOG502QVY3"
curl -sL "http://eggnogapi5.embl.de/nog_data/json/go_terms/ENOG502QVY3"
```

Prefer these direct URL patterns. Do **not** rely on fetching the EggNOG website
UI (often blocked); call the REST paths above directly.

## Agent procedure

1. Confirm the NOG/COG id.
2. Request only needed attributes.
3. Save under `analysis/annotation-eggnog-api/`.
4. For proteome-scale annotation use `shotgun-eggnog` (local mapper), not this API alone.
