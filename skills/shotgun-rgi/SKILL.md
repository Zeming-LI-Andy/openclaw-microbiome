---
name: shotgun-rgi
description: >
  Screen assemblies or proteins for antimicrobial resistance genes with CARD RGI.
runtime: rgi
conda_env: rgi
tools:
  - rgi
  - python
---

# Shotgun AMR (CARD RGI)

## Runtime

| Field | Value |
|-------|-------|
| Runtime id | `rgi` |
| Conda env | `rgi` |

DB: look up paths in `registry/references.yaml`. If missing, ask the user —
do not invent.

## Reference script (`scripts/`)

`scripts/annotate_rgi.py` — **reference only** for protein-mode RGI. Adapt for
contigs (`-t contig`) or different RGI flags as needed.

```bash
export CARD_JSON=<resolved>
python skills/shotgun-rgi/scripts/annotate_rgi.py \
  --protein <job>/stage/proteins.faa \
  --output-dir <job>/analysis/shotgun-rgi \
  --threads 8
```

Do not invent AMR hits if CARD / RGI is unavailable.

## Agent procedure

1. Stage contigs or protein FASTA under the session `stage/`.
2. Resolve the DB path from `registry/references.yaml` (ask if missing); load /
   local setup per `rgi --help` / `rgi load` if needed.
3. Adapt the reference script or `conda run -n rgi rgi …`.
4. Write under `analysis/shotgun-rgi/`.

## Ask the user when unknown

- Input type (contig vs protein)
- Alignment tool / loose vs strict criteria
