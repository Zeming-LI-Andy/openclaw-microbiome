---
name: shotgun-gene-catalog
description: >
  Predict ORFs with Prodigal and build a non-redundant gene/protein catalog
  with CD-HIT (contigs → FASTA → cluster).
runtime: eggnog_mapper
conda_env: eggnog_mapper
tools:
  - prodigal
  - cd-hit
  - python
---

# Shotgun gene catalog (Prodigal → CD-HIT)

## Runtime

| Stage | Runtime id (registry) | Default conda env |
|-------|----------------------|-------------------|
| `predict` | `eggnog_mapper` | `eggnog_mapper` |
| `cluster` | `host` | `mgx-base` |

No reference DBs required.

## Reference script (`scripts/`)

Reference (path relative to this skill): `scripts/build_gene_catalog.py`.

**Copy/adapt** it into the session job; do not run against the skill tree as
cwd. After copying to e.g. `<job>/analysis/shotgun-gene-catalog/`:

```bash
python build_gene_catalog.py predict \
  --contigs <job>/stage/contigs.fasta \
  --output-dir <job>/analysis/shotgun-gene-catalog/predict

python build_gene_catalog.py cluster \
  --input <job>/analysis/shotgun-gene-catalog/predict/proteins.faa \
  --output-dir <job>/analysis/shotgun-gene-catalog/cluster \
  --identity 0.95 --coverage 0.9
```

Nucleic-acid catalog (genes `.ffn`):

```bash
python build_gene_catalog.py cluster \
  --input <job>/analysis/shotgun-gene-catalog/predict/genes.ffn \
  --output-dir <job>/analysis/shotgun-gene-catalog/cluster \
  --mode nucleotide --identity 0.95 --coverage 0.9
```

Run **predict** and **cluster** as separate steps (see `CODING.md`). Downstream
functional annotation: `shotgun-eggnog` (and related skills) on the NR protein
FASTA. This skill does **not** map reads for abundance.

## Agent procedure

1. Stage contigs (or an existing protein/gene FASTA) under `stage/`.
2. If starting from contigs: copy/adapt `scripts/build_gene_catalog.py` into the
   job and run `predict` (or equivalent `conda run -n eggnog_mapper prodigal …`).
3. Run `cluster` on `.faa` (default) or `.ffn` (`--mode nucleotide`).
4. Write under `analysis/shotgun-gene-catalog/`.

## Ask the user when unknown

- Input type (contigs vs existing protein/gene FASTA)
- Protein vs nucleotide clustering
- CD-HIT identity / coverage thresholds
