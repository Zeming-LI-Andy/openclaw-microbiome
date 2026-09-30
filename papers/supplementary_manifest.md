# Provisional supplementary-results manifest

This file tracks result tables and records that may be cited from the main
text.  The identifiers are stable working names rather than final Supplementary
Table numbers; assign S-numbers only after the main-text figures and tables are
frozen.

| Working identifier | Contents | Main Results section |
|---|---|---|
| `datasets-and-analysis-scope` | Dataset accessions, biological samples, sequencing libraries, groups, data volumes, requested analyses and completed stages for all three case studies | Case-study overview |
| `case1-16s-statistics` | Case 1 alpha/beta-diversity tests, PERMANOVA/PERMDISP results, differential-abundance effect sizes and adjusted P values | Case study 1 |
| `case1-metaphlan-version-sensitivity` | MetaPhlAn2 versus MetaPhlAn3 database builds, detection prevalence, abundance, effect sizes and adjusted P values for *P. putida* and *Sphingopyxis unclassified* | Case study 1 |
| `case3-species-and-function-tests` | CRC species, gene-family and KO differential-analysis results | Case study 2 |
| `case3-classifier-folds` | Features, nested cross-validation splits, fold-level metrics, pooled metrics and confidence intervals | Case study 2 |
| `case4-mag-catalogue` | MAG quality, dereplication clusters, GTDB taxonomy and abundance by enrichment | Case study 3 |
| `case4-functional-annotations` | Focal MAG identifiers, annotation database versions, matched genes and module-level CDS counts | Case study 3 |
| `robustness-session-results` | All 27 sessions: model, prompt granularity, run, job ID, completion rubric, interventions, runtime and failure mode | Robustness |
| `robustness-output-concordance` | Pairwise Shannon correlations, Mantel tests, Procrustes comparisons and analytical choices across repeats | Robustness |
| `hitl-intervention-log` | Timestamped user feedback, interaction mode, affected pending steps, plan revisions and transcript evidence | Human-in-the-loop evaluation |
| `hitl-operational-outcomes` | Compute preservation, feedback incorporation, automatic resumption, revised-plan fidelity, exactly-once execution and latency for every session | Human-in-the-loop evaluation |
| `ablation-session-results` | Full, no-patch, no-skills and no-coding session-level completion and process metrics | Ablation |
| `software-and-reference-versions` | Tool, environment, reference database, build/release, command and case-study use | Methods and all Results sections |

## Main-text placeholder convention

Until final S-numbers are assigned, place a nearby LaTeX comment using the
working identifier, for example:

```tex
% SUPPLEMENTARY PLACEHOLDER: case1-metaphlan-version-sensitivity
```

Do not create unresolved `\ref{}` commands in `main.tex`.  Once the
supplementary document is assembled, replace each comment with its final
`Supplementary Table~S...` or `Supplementary Fig.~S...` citation.

## Prepared table fragments

- `datasets-and-analysis-scope`: included at the end of `main.tex` as Supplementary Table S1 (`tab:cases-overview`). The earlier standalone fragment is retained as a draft; `main.tex` is the authoritative version. Supplementary tables and figures are numbered independently with an S prefix.
