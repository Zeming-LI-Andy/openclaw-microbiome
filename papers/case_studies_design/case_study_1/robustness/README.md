# Case study 1 — robustness

3 models × 3 prompt granularities × 3 runs. One new OpenClaw conversation per replicate; paste one of `prompt_*.md`.

## `stage/`

Frozen inputs for every run. Copy this tree into the session job `stage/` (do not point the agent at `PRJNA777724/`).

```
stage/16s/          ASV table, rep-seqs, rooted tree, DADA2 stats, metadata
stage/shotgun/      sample table
stage/shotgun/reads 20% subsampled KneadData paired FASTQ (hardlinked; 36 libraries)
```

Do not re-run DADA2, phylogeny, or KneadData. Do not reuse precomputed diversity/MetaPhlAn under `PRJNA777724/`.

| Prompt | Granularity |
|--------|-------------|
| `prompt_detailed.md` | metrics, tests, figure types |
| `prompt_medium.md` | analysis goals only |
| `prompt_simple.md` | scientific question only |
