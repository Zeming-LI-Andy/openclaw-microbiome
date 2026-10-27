# Supplementary materials manifest

This manifest records the supplementary materials currently associated with
`main.tex`. The numbering below follows the order in the compiled manuscript.
If figures or tables are reordered, update this file together with their LaTeX
labels and citations.

`main.tex` is authoritative for the contents and numbering of Supplementary
Figures and Supplementary Tables. Supplementary Data 1 is maintained as a
separate workbook. No separate "Supplementary Data 2 -- Robustness and
ablation" workbook is currently planned; session-level robustness and ablation
records will instead accompany the article archive.

## Supplementary Information in `main.tex`

### Figures

| Number | LaTeX label | File | Contents | Main-text use |
|---|---|---|---|---|
| Supplementary Figure S1 | `fig:tomato-enrichment` | `figures/Case-study-1-Fig2_16s_genus_enrichment.png` | Genera enriched in both resistant tomato cultivars across sampling conditions | Case 1 results |
| Supplementary Figure S2 | `fig:robustness-models` | `figures/case1_completion_models.png` | Task completion and quantitative-output comparisons among models within each prompt level | Robustness results |
| Supplementary Figure S3 | `fig:robustness-prompts` | `figures/by_prompt_models.png` | Quantitative-output comparisons among prompt levels within each model | Robustness results |

### Tables

| Number | LaTeX label | Contents | Main-text use |
|---|---|---|---|
| Supplementary Table S1 | `tab:cases-overview` | Dataset accessions, library counts, analysis routes and evaluation targets for the three case studies | Case-study overview and design |
| Supplementary Table S2 | `tab:software-versions` | Software and reference-database versions recorded in archived case-study outputs | Case-study methods; a main-text citation still needs to be added |
| Supplementary Table S3 | `tab:agent-capabilities` | Scope comparison of MicroBioAgent with related bioinformatics agents | Discussion |
| Supplementary Table S4 | `tab:da-model-methods` | DESeq2 sessions and shared entries included in cross-model differential-abundance comparisons | Robustness Results, Methods and Supplementary Figure S2 |
| Supplementary Table S5 | `tab:da-prompt-methods` | Methods, included sessions and shared entries for detailed-versus-medium prompt comparisons | Robustness Results, Methods and Supplementary Figure S3 |

## Supplementary Data 1

**Submission file:** `supplementary/Supplementary Data 1 — Case studies.xlsx`

**Scope:** Sample-level accessions and numerical results from the three case
studies. This workbook is supporting data for the case studies; it is not the
source-data package for the robustness and ablation experiments.

| Sheet | Contents | Related manuscript section |
|---|---|---|
| `sample_accessions` | BioProject, assay, sample and run-accession mapping for all 230 sequencing libraries | Case-study design; Supplementary Table S1 |
| `case1_16s_statistics` | Shannon, PERMANOVA and PERMDISP results for Case 1 | Case 1 results |
| `case1_metaphlan_versions` | Recorded MetaPhlAn2/3 evidence for the two species highlighted in the source study | Case 1 profiler-version follow-up |
| `case1_16s_differential` | Genus-level resistant-versus-susceptible differential results | Case 1 results; Supplementary Figure S1 |
| `case1_shotgun_differential` | Species-level resistant-versus-susceptible differential results | Case 1 results |
| `case2_community_statistics` | Bray–Curtis PERMANOVA for CRC status, disease stage, sex, age and BMI | Case 2 results |
| `case2_species_tests` | CRC species-association direction and adjusted significance | Case 2 results |
| `case2_cooccurrence_edges` | Spearman correlations among the ten differentially abundant species, with raw P, BH q, and the reported-network flag | Case 2 co-occurrence network |
| `case2_function_tests` | Gene-family and KO significance results | Case 2 functional analysis |
| `case2_classifier_folds` | Fold-level performance, pooled performance and selected classifier features | Case 2 classifier results |
| `case3_mag_catalogue` | Quality, taxonomy and cluster membership of the 75 MAGs retained after dereplication at 95% ANI | Case 3 results |
| `case3_mag_abundance` | Species- and genus-resolved abundances aggregated from the representative MAGs across the six enrichment cultures | Case 3 abundance analysis |
| `case3_functional_annotations` | Mapping of source-study taxa to GTDB taxa and gene counts for the three functional categories in 11 annotated 95% ANI representative MAGs; `Achromobacter sp.` is represented by two ANI clusters | Case 3 functional analysis |

### Open checks before submission

1. Align the Case 1 MetaPhlAn2 statement in the Results with the comparisons
   recorded in `case1_metaphlan_versions`. The workbook supports detection of
   both reported taxa, but resistant enrichment is comparison- and
   timepoint-specific rather than significant in every contrast.
2. Add a main-text citation to Supplementary Table S2
   (`tab:software-versions`).
3. Clarify in the Supplementary Figure S1 caption that the enrichment rule
   uses nominal, unadjusted `P < 0.05`.
4. Revise the Supplementary Figure S2 caption so that Shannon, weighted
   UniFrac and relative-abundance points are described as sample-, sample-pair-
   and sample--taxon-level values averaged across completed sessions,
   respectively.
5. Add a workbook README/data dictionary defining sheet scope, fields,
   missing values, statistical adjustment, the distinction between raw `P`
   and adjusted `q`, and the relation among MAG identifiers, dereplication
   clusters and representative MAGs.

## Article-archive records

The following records support reproducibility and audit of the evaluation but
are not planned as an additional Supplementary Data workbook.

| Archive record | Contents | Current source location |
|---|---|---|
| Robustness sessions | All 27 model--prompt sessions, job IDs, task-completion results, selected methods and statistical-comparison inputs | `case_studies_design/case_study_1/robustness/` |
| End-to-end ablation sessions | Full and no-patch per-session output completion, method adherence, model/tool calls and token accounting | `case_studies_design/case_study_1/ablation/` |
| Human-guidance evaluation | Standardized intervention prompts, transcripts, process evidence, plan-update outcomes and automatic-reactivation outcomes | `case_studies_design/case_study_1/hitl_patch_ablation/` |
| Analysis and figure code | Scripts used to generate manuscript statistics, tables and figures | Project repository and accompanying article archive |

The Data availability and Code availability sections should point to the
immutable article archive once its DOI or accession is assigned.

## Files not intended for submission

- `supplementary/datasets-and-analysis-scope.tex` is an earlier draft of
  Supplementary Table S1. The table embedded in `main.tex` is authoritative.
- Working reports and intermediate exports under `results_summary_report/`,
  `tmp/` and `build/` are not supplementary deliverables.
