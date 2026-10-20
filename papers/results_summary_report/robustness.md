# Robustness experiment — Case 1

**Manuscript role:** Results robustness; Methods evaluation.  
**Base case:** Case 1, tomato rhizosphere bacterial-wilt (NCBI BioProject PRJNA777724; Yin et al., *Microbiome* 2022).  
**Analysis prompt set:** `papers/case_studies_design/case_study_1/robustness/prompt_{detailed,medium,simple}.md`  
**Staged inputs:** `papers/case_studies_design/case_study_1/robustness/stage/`  
**Not used:** the full-pipeline `papers/case_studies_design/case_study_1/prompt.md` (raw FASTQ → DADA2).

The protocol further down is how the 27 sessions were run. The results below are only what is drawn in these two figures and listed in these two tables:

- `papers/case_studies_design/case_study_1/robustness/figures/case1_completion_models.png`
- `papers/case_studies_design/case_study_1/robustness/figures/by_prompt_models.png`
- `papers/case_studies_design/case_study_1/robustness/tables/da_model_method_summary.tsv`
- `papers/case_studies_design/case_study_1/robustness/tables/da_prompt_method_summary.tsv`

Numeric values are taken from the tables those figures are drawn from: `task_completion_summary.tsv`, `task_completion_by_session.tsv`, `model_distribution_tests.tsv`, `model_distribution_coverage.tsv`, `composition_da_distribution_tests.tsv`, `model_deseq2_comparison_tests.tsv`, `model_deseq2_comparison_coverage.tsv`, `prompt_comparison_tests.tsv`, `16s_da_by_prompt_tests.tsv`, and `shotgun_da_by_prompt_tests.tsv`. Display names on the figures are GLM-Flash, DeepSeek-Flash, and DeepSeek-Pro.

---

## How the two figures are built

`case1_completion_models.png` has two panels.

- **a.** Six completion heatmaps. Each cell is the percentage of three runs, also printed as *n*/3. Rows are GLM-Flash, DeepSeek-Flash, DeepSeek-Pro. Columns are Detailed, Medium, Simple. A run counts as complete when a numeric result exists. A figure alone does not count. The six tasks are 16S alpha diversity, 16S beta diversity, 16S genus-level taxonomic profiling, 16S differential abundance, shotgun species-level taxonomic profiling, and shotgun differential abundance.
- **b.** Between-model distributions, with one box per model inside each prompt. The upper 2×2 is 16S Shannon, pairwise weighted UniFrac distance, 16S genus relative abundance, and shotgun species relative abundance. The lower row is three DESeq2 comparisons: 16S differential abundance at Detailed, 16S differential abundance at Medium, and shotgun differential abundance at Detailed.

`by_prompt_models.png` is one 3×6 grid. Rows are DeepSeek-Pro (a), DeepSeek-Flash (b), and GLM-Flash (c). Columns are 16S Shannon, weighted UniFrac distance, 16S genus relative abundance, shotgun species relative abundance, 16S differential abundance, and shotgun differential abundance. The first four columns have Detailed, Medium, and Simple. The two differential-abundance columns have Detailed and Medium only.

Brackets on both figures are pairwise two-sided Mann–Whitney U tests on the values that enter the boxes. A pair is tested only when both groups have at least five values; every comparison in these two figures meets that bar. Holm adjustment is inside that panel (three pairs when three groups are present; one pair when only Detailed and Medium are compared, so the Holm *P* equals the raw *P*). The Holm step-down is the usual one: sort the raw *P* values, multiply the *k*-th by the number of tests still remaining, then enforce monotonicity and cap the result at 1. Stars are Holm *P* < 0.05 (\*), < 0.01 (\*\*), < 0.001 (\*\*\*); otherwise the bracket is n.s. These brackets compare distributions of reported values. Samples, sample pairs, and taxa come from one experiment and are not independent replicates. A bracket is not a new biological differential-abundance test. The boxes hide points beyond the whiskers. The test and the reported median use every value, including those hidden points.

Files are read from each session’s `analysis/` directory. Directories named retired or superseded are skipped, as are `bowtie2`, `bt2`, `bt2out`, `mpa_db`, `provenance`, `dist`, and `node_modules`. A numeric table is a `.tsv`, `.csv`, or `.txt` file. A QIIME2 `.qza` is read only for Shannon and for a distance matrix.

### Task completion

A run is complete when the numeric artifact below exists. A figure alone does not count. The heatmap prints the percentage of the three runs, rounded to an integer, and the count as *n*/3. GLM-Flash Detailed shotgun is 2/3 and is shown as 67%.

| Task | What counts as complete |
|---|---|
| 16S alpha diversity | A per-sample Shannon vector with at least 30 non-missing samples. |
| 16S beta diversity | Any one square sample distance matrix with at least 30 samples. Weighted UniFrac, Bray–Curtis, and unweighted UniFrac all qualify. Jaccard does not. |
| 16S genus-level taxonomic profiling | A sample-by-genus abundance table with at least 30 samples and 5 genera. |
| 16S differential abundance | A `.tsv` or `.csv` of at least 5 rows, on a differential-abundance path, with taxon names and a *p*, *q*, log2 fold change, coefficient, or LDA column. The table has to be genus-level or an amplicon table, not a shotgun-only species table. Pathway, PICRUSt, HUMAnN, Bowtie, feature, distance-matrix, and DADA2 paths are skipped. |
| Shotgun species-level taxonomic profiling | The same abundance rule at species level, at least 30 samples and 5 species, or at least 30 per-library MetaPhlAn profiles that contain species rows. |
| Shotgun differential abundance | The same differential-abundance rule at species level. An amplicon-only or genus-only table does not count. |

This pass/fail is wider than the distributions below. Beta completion accepts whichever distance matrix the run produced. The beta boxes use weighted UniFrac only. Differential-abundance completion accepts any qualifying tool. The boxes below accept only the tool fixed for that comparison.

### 16S Shannon

One Shannon vector is taken from each session. A file qualifies when its name contains `shannon`, or when the file is `alpha-diversity.tsv`. Faith, observed-feature, and evenness files are not used unless the file name itself contains `shannon`. A `.qza` is read only when its name contains `shannon`; the table inside the archive is used. Among the vectors with at least 10 samples, the one closest to 60 samples is kept, and a text table is preferred over a `.qza` at the same size. Duplicate sample ids keep the first value.

Zeros are then dropped. Coverage of these 27 sessions records 60 Shannon values in every session and no zeros, so nothing is removed by that filter. Within one model and one prompt, the three sessions are averaged per sample. Samples missing from a session are omitted from that average rather than filled with zero.

The between-model panel then keeps samples present for all three models at that prompt. The between-prompt panel starts from those model-shared means and keeps samples present at every prompt of that model. Both intersections retain 60 samples here, which is why every Shannon box has *n* = 60.

### Weighted UniFrac

Distance files are classified from the path: weighted UniFrac, unweighted UniFrac, or Bray–Curtis. Jaccard is ignored. A `.qza` contributes its `distance-matrix.tsv`. A text file is read when its name contains `distance`, `unifrac`, or `bray`. The matrix must be square, with at least 10 samples shared by the rows and the columns. For each metric, the matrix closest to 60 samples is kept, and a text table is preferred over a `.qza` at the same size.

The boxes do not use that choice. They use the weighted UniFrac matrix only, including when the run also wrote Bray–Curtis or unweighted UniFrac. The upper triangle is taken so each unordered pair appears once. The two triangles are averaged where both are finite, which makes a slightly asymmetric export into one distance. The diagonal is omitted. A non-finite distance is omitted. The pair id is the two sample ids in alphabetical order.

Within one model and one prompt, the three sessions are averaged per pair, with no zero-fill. The between-model panel keeps pairs present for all three models. The between-prompt panel then keeps pairs present at every prompt of that model. Both intersections retain 1,770 pairs, which is every unordered pair among 60 samples, so every weighted UniFrac box has *n* = 1,770.

### Genus and species relative abundance

One composition table is taken from each session.

Genus candidates are text tables whose path contains `genus` and does not contain shotgun, MetaPhlAn, or species. Species candidates contain `species` or `merged_abundance` and do not contain `16s` or `genus`. Differential-abundance, pathway, phylum, class, order, and family tables are not candidates. A candidate also has to look like an abundance table (`relab`, `relative`, `composition`, `count`, `proportion`, or `genus_table`).

The table is turned so that rows are samples. A sample id is recognized only when it matches a cultivar–timepoint–replicate pattern such as `A57-T1-RS1`. At least 30 samples are required. Genus and species names are taken from a `g__` or `s__` label when that label is present, otherwise from the last taxonomy token. The name is lowercased and spaces become underscores. Blank names, `unclassified`, `uncultured`, `incertae_sedis`, and species labels that end in `_sp` or are shorter than five characters are dropped. Strain labels (`t__`) are not species. Duplicate taxon columns are summed. Duplicate sample rows keep the first.

A merged table is converted before taxon names are filtered. Non-numeric cells become 0 and negative values are clipped to 0. The whole table is classified once. If the median row sum is at most 1.5, the table is already relative abundance and its values are kept. If the maximum is at most 100 and the median row sum is between 50 and 150, it is a percentage table and is divided by 100. Any other large-sum table is raw counts: each sample is divided by its own row total, including taxa that the name filter will drop. Names are filtered after that conversion. Blank names, and the other names dropped above, leave the table, and the remaining values are not scaled to 1. Zero abundances are dropped.

A single-sample file is handled on its own. MetaPhlAn `*_profile.txt` files are the single-sample species source. Each file is one sample. The `UNKNOWN` line is ignored when reading the file's scale, because that line is sometimes a percentage while the clade lines are proportions. A file whose clade values exceed 1.5 and stay at most 100 is divided by 100. A file whose clade values stay at most 1.5 is kept as stored. A file whose clade values exceed 100 is treated as counts and each species is divided by the sum of the species rows in that file. Species that fail the name filter are removed after this conversion, without a second scaling. Files are then placed side by side. Counts from different samples are not added into one denominator.

If no genus table passes, ASV counts are collapsed with a taxonomy table, or a 16S BIOM whose observations already carry `g__` labels is collapsed. Each genus is divided by the full sample total, including reads without a genus name, and is not scaled again after unnamed reads are left out. If no species table passes, the MetaPhlAn profiles above are merged. At least 30 profiles are required.

The chosen genus table is the one whose sample count is closest to 60; the chosen species table is the one closest to 36. Ties go to the table with more taxa.

Sessions of one group are then averaged per sample–taxon pair. If a session has the sample but not the taxon, that taxon contributes 0 to the average. This zero-fill is used only for composition. A pair whose average is 0 is dropped. Each group is then restricted to pairs whose session-mean relative abundance is at least 0.05. The box keeps pairs that still pass that floor in every group being compared, so the logarithmic axis has no non-positive values.

In the between-model panel the groups are the three models inside one prompt. In the between-prompt panel the groups are Detailed, Medium, and Simple inside one model. The two intersections are different sets, so the *n* of a composition box is not transferable from one figure to the other.

### Differential-abundance values

- Model DESeq2 panels: one DESeq2 log2 fold change per taxon per session, then the mean across sessions that ran DESeq2. No zero-fill. A taxon enters the box only when that value is finite for all three models. 16S is genus. Shotgun is species.
- Prompt differential-abundance columns: one log2 fold change per taxon per session, then the mean across sessions that ran the method fixed for that model. A taxon enters the box only when it is finite at both Detailed and Medium. Simple is not in these columns.

Session counts in the two method tables are replicates that entered that mean, written as *n*/3. They are smaller than the completion counts wherever a finished differential-abundance run used a table that this comparison does not include.

### Why the two differential-abundance comparisons use different methods

The bracket compares distributions, so every box in one panel has to be the same kind of number. The two figures hold different factors fixed, and the runs did not produce the same tool in every cell. The method is whatever satisfies that constraint. It is not a preferred tool applied to every cell.

**Between models, prompt held fixed.** The three boxes are GLM-Flash, DeepSeek-Flash, and DeepSeek-Pro. A panel is drawn only when all three models produced the same statistic at that prompt. Genus-level DESeq2 log2 fold change meets that test for 16S Detailed and 16S Medium. Species-level DESeq2 meets it for shotgun Detailed. Those are the three panels in `case1_completion_models.png`. Shotgun Medium is omitted, and `da_model_method_summary.tsv` records “—”, because no differential-abundance tool is present in all three models at that prompt. A tool that only some sessions of a model also ran, including MaAsLin3, LEfSe, Wilcoxon, and Mann–Whitney, stays out of this panel. Putting it in would mix two statistics inside one box, or would drop a model from the comparison.

**Between prompts, model held fixed.** The two boxes are Detailed and Medium inside one model. Simple stays in the Shannon, UniFrac, and composition columns because those three products have one definition at every prompt. The differential-abundance columns are a Detailed-versus-Medium comparison, so Simple sessions are not included. The statistic has to be one that the same model produced under both prompts.

For 16S, genus-level DESeq2 meets that test in every model, so all three rows use DESeq2. An ASV-only DESeq2 table is left out, which is why DeepSeek-Flash Detailed replicate 3 counts as complete on the heatmap and does not enter the genus comparison. A table whose names are mostly long hexadecimal ASV identifiers is also dropped, so those identifiers are not treated as genus names.

For shotgun, no one tool was produced by every model under both prompts, so the row follows the tool that model did produce twice. GLM-Flash has species-level DESeq2 at Detailed (replicates 1 and 3) and at Medium (replicate 2). DeepSeek-Flash does not have shotgun DESeq2 at both prompts; the tool present at both is Mann–Whitney U (Detailed replicate 3 and Medium replicate 3). DeepSeek-Pro does not have shotgun DESeq2 at both prompts; the tool present at both is Wilcoxon (Detailed replicate 2 and Medium replicate 2). The three shotgun log2 fold changes are therefore different quantities. They stay on separate y axes and are not tested against each other. This is also why the shotgun replicates in `da_prompt_method_summary.tsv` are not the shotgun replicates in the between-model DESeq2 panel: DeepSeek-Flash’s DESeq2 replicates are 1 and 2, and DeepSeek-Pro’s DESeq2 replicate is 1.

**How several tables inside one session become one number.** Both comparisons start the same way. A file is read only when it is the assay being compared (16S or shotgun), it is not in a superseded directory, and its name does not contain `annotated`. DESeq2 is recognized by “deseq” in the path, by a `log2FoldChange` column, or by `lfcSE` together with `baseMean`, so a DESeq2 table whose name does not contain “deseq” still counts. The effect column is `log2FoldChange`, `log2FC`, or another log2 fold-change column that is not a standard error. Rows that name a contrast are kept when that contrast refers to resistance, phenotype, HG64, HF12, or the susceptible cultivars; a table with no contrast column keeps every row. If a MaAsLin-style `model` column contains an abundance model, only those abundance rows are kept. A table is dropped when more than 20% of its taxon names are hexadecimal strings of 16 or more characters. Inside one table, repeated rows of the same taxon become their median log2 fold change.

The comparisons then part company, because a session often wrote either one pooled table or a pile of single-contrast tables.

- Between-model DESeq2 uses the pooled table when the session has one. A file whose name contains `all_comparison`, `all-result`, `all_result`, or `combined` is that pooled table, and the largest such file is kept if several exist. The pooled table is the session’s DESeq2 result, so one contrast is not asked to stand for the others. If the session has no pooled table and has more than one contrast table, the median across those tables is the session value, for the same reason. A single contrast table is used as it is. A DESeq2 table is kept only when at least half of its log2 fold changes are finite.
- Between-prompt DESeq2 uses one table per session: the largest table that passes the rank filter and the same half-finite rule. It does not take the median across contrast files. Where a session stored only separate contrasts, this comparison therefore follows the contrast that retained the most taxa, while the between-model comparison follows the median of those contrasts.
- Between-prompt Mann–Whitney collects every shotgun species table with a U statistic (`U`, `statistic_U`, or `p_mwu`), skips paths marked genus or Welch, and takes the median across those tables. These tables are not held to the half-finite cutoff.
- Between-prompt Wilcoxon keeps one shotgun species table: the largest whose name marks an all-comparison or a Wilcoxon result and whose columns include a U statistic. It is not held to the half-finite cutoff either.

Across sessions, the mean uses only the sessions listed for that method, and a taxon missing from one of those sessions is left missing. The between-model box then requires the taxon to be finite in all three models. The between-prompt box requires it to be finite at both prompts of that one model. Those are different intersections, which is why shotgun Detailed can be 43 species in the model panel and 14, 39, or 9 species in the prompt rows.

---

## Task completion

Of 162 task-runs (6 tasks × 27 sessions), 160 are complete. Every 16S task is 3/3 for every model and every prompt.

The two incomplete task-runs are the same session. GLM-Flash, Detailed, replicate 2 has no scored numeric artifact for shotgun species-level taxonomic profiling or for shotgun differential abundance. Both heatmap cells are 2/3, shown as 67%. Every other shotgun cell is 3/3.

| Task | Cell that is not 3/3 | Complete runs |
|---|---|---|
| Shotgun species-level taxonomic profiling | GLM-Flash, Detailed | 2/3 |
| Shotgun differential abundance | GLM-Flash, Detailed | 2/3 |

Completion of a differential-abundance task means some numeric DA table exists. It does not mean that table entered the DESeq2, Wilcoxon, or Mann–Whitney comparison below.

---

## Between-model distributions

Panel b of `case1_completion_models.png`. Medians are the medians of the plotted values. Model order in each pair follows the test table: GLM-Flash, DeepSeek-Flash, DeepSeek-Pro.

### 16S Shannon and weighted UniFrac

All 18 between-model tests (Shannon and weighted UniFrac, three prompts, three pairs) have Holm-adjusted *P* = 1.

Shannon medians (*n* = 60):

| Prompt | GLM-Flash | DeepSeek-Flash | DeepSeek-Pro |
|---|---:|---:|---:|
| Detailed | 9.586 | 9.830 | 9.825 |
| Medium | 9.828 | 9.827 | 9.825 |
| Simple | 9.831 | 9.807 | 9.832 |

Weighted UniFrac medians (*n* = 1,770):

| Prompt | GLM-Flash | DeepSeek-Flash | DeepSeek-Pro |
|---|---:|---:|---:|
| Detailed | 0.303 | 0.301 | 0.301 |
| Medium | 0.301 | 0.301 | 0.301 |
| Simple | 0.301 | 0.302 | 0.301 |

### 16S genus relative abundance

| Prompt | *n* | GLM-Flash median | DeepSeek-Flash median | DeepSeek-Pro median | Pair | *U* | Raw *P* | Holm *P* | Bracket |
|---|---:|---:|---:|---:|---|---:|---:|---:|---|
| Detailed | 32 | 0.322 | 0.209 | 0.233 | GLM-Flash vs DeepSeek-Flash | 710 | 0.00800 | 0.0240 | \* |
| Detailed | 32 | 0.322 | 0.209 | 0.233 | GLM-Flash vs DeepSeek-Pro | 685 | 0.0205 | 0.0411 | \* |
| Detailed | 32 | 0.322 | 0.209 | 0.233 | DeepSeek-Flash vs DeepSeek-Pro | 459 | 0.481 | 0.481 | n.s. |
| Medium | 25 | 0.347 | 0.346 | 0.221 | GLM-Flash vs DeepSeek-Flash | 325 | 0.816 | 0.816 | n.s. |
| Medium | 25 | 0.347 | 0.346 | 0.221 | GLM-Flash vs DeepSeek-Pro | 494 | 4.45×10⁻⁴ | 1.33×10⁻³ | \*\* |
| Medium | 25 | 0.347 | 0.346 | 0.221 | DeepSeek-Flash vs DeepSeek-Pro | 492 | 5.14×10⁻⁴ | 1.33×10⁻³ | \*\* |
| Simple | 46 | 0.150 | 0.245 | 0.154 | GLM-Flash vs DeepSeek-Flash | 1,006.5 | 0.690 | 1 | n.s. |
| Simple | 46 | 0.150 | 0.245 | 0.154 | GLM-Flash vs DeepSeek-Pro | 985 | 0.571 | 1 | n.s. |
| Simple | 46 | 0.150 | 0.245 | 0.154 | DeepSeek-Flash vs DeepSeek-Pro | 1,058 | 1 | 1 | n.s. |

At Detailed, GLM-Flash’s genus relative abundances sit above both DeepSeek models. At Medium, DeepSeek-Pro’s median (0.221) sits below GLM-Flash (0.347) and DeepSeek-Flash (0.346). At Simple, no pair passes Holm adjustment.

### Shotgun species relative abundance

| Prompt | *n* | GLM-Flash median | DeepSeek-Flash median | DeepSeek-Pro median | Pair | *U* | Raw *P* | Holm *P* | Bracket |
|---|---:|---:|---:|---:|---|---:|---:|---:|---|
| Detailed | 97 | 0.212 | 0.223 | 0.215 | GLM-Flash vs DeepSeek-Flash | 4,770 | 0.868 | 1 | n.s. |
| Detailed | 97 | 0.212 | 0.223 | 0.215 | GLM-Flash vs DeepSeek-Pro | 4,750 | 0.908 | 1 | n.s. |
| Detailed | 97 | 0.212 | 0.223 | 0.215 | DeepSeek-Flash vs DeepSeek-Pro | 4,677 | 0.945 | 1 | n.s. |
| Medium | 6 | 0.483 | 0.0708 | 0.185 | GLM-Flash vs DeepSeek-Flash | 36 | 0.00216 | 0.00649 | \*\* |
| Medium | 6 | 0.483 | 0.0708 | 0.185 | GLM-Flash vs DeepSeek-Pro | 30 | 0.0649 | 0.0649 | n.s. |
| Medium | 6 | 0.483 | 0.0708 | 0.185 | DeepSeek-Flash vs DeepSeek-Pro | 0 | 0.00216 | 0.00649 | \*\* |
| Simple | 62 | 0.155 | 0.173 | 0.454 | GLM-Flash vs DeepSeek-Flash | 1,541 | 0.0572 | 0.0572 | n.s. |
| Simple | 62 | 0.155 | 0.173 | 0.454 | GLM-Flash vs DeepSeek-Pro | 425 | 7.51×10⁻¹⁴ | 2.25×10⁻¹³ | \*\*\* |
| Simple | 62 | 0.155 | 0.173 | 0.454 | DeepSeek-Flash vs DeepSeek-Pro | 559 | 9.83×10⁻¹² | 1.97×10⁻¹¹ | \*\*\* |

At Detailed, the three species-abundance distributions are not separated. At Medium, six shared sample–species pairs remain after the 0.05 floor. GLM-Flash’s median is 0.483, DeepSeek-Flash’s is 0.0708, and DeepSeek-Pro’s is 0.185. GLM-Flash vs DeepSeek-Pro stays n.s. At Simple, DeepSeek-Pro’s median (0.454) sits above GLM-Flash (0.155) and DeepSeek-Flash (0.173); GLM-Flash vs DeepSeek-Flash stays n.s.

---

## DESeq2 shared across models

Lower row of panel b, with `da_model_method_summary.tsv`. A taxon is plotted only when all three models have a finite DESeq2 log2 fold change. Shotgun Medium is absent from the figure and is recorded as “—” in the table: the three models did not share one differential-abundance method at that prompt.

Sessions that entered the mean:

| Analysis | Model | Method | Detailed | Medium |
|---|---|---|---|---|
| 16S rRNA gene, genus | DeepSeek-Pro | DESeq2 | 1/3 | 1/3 |
| 16S rRNA gene, genus | DeepSeek-Flash | DESeq2 | 2/3 | 2/3 |
| 16S rRNA gene, genus | GLM-Flash | DESeq2 | 3/3 | 1/3 |
| Shotgun metagenome, species | DeepSeek-Pro | DESeq2 | 1/3 | — |
| Shotgun metagenome, species | DeepSeek-Flash | DESeq2 | 2/3 | — |
| Shotgun metagenome, species | GLM-Flash | DESeq2 | 2/3 | — |

Replicates behind those counts:

- 16S genus, Detailed: GLM-Flash 1, 2 and 3; DeepSeek-Flash 1 and 2; DeepSeek-Pro 1.
- 16S genus, Medium: GLM-Flash 2; DeepSeek-Flash 1 and 3; DeepSeek-Pro 2.
- Shotgun species, Detailed: GLM-Flash 1 and 3; DeepSeek-Flash 1 and 2; DeepSeek-Pro 1.

GLM-Flash Detailed shotgun is 2/3 here for the same reason it is 2/3 on the heatmap: replicate 2 has no shotgun result. The other gaps are runs that finished a differential-abundance task with a table this DESeq2 comparison does not use. The genus comparison omits ASV-only DESeq2 tables; DeepSeek-Flash Detailed replicate 3 is the 16S run left out by that rule, even though the heatmap marks its 16S differential-abundance task complete.

Taxa reported by each model before the three-model intersection, then the number that enter the box:

| Comparison | GLM-Flash taxa | DeepSeek-Flash taxa | DeepSeek-Pro taxa | Taxa in the box |
|---|---:|---:|---:|---:|
| 16S genus, Detailed | 1,012 | 1,124 | 545 | 216 |
| 16S genus, Medium | 508 | 852 | 431 | 332 |
| Shotgun species, Detailed | 43 | 144 | 148 | 43 |

On shotgun Detailed, GLM-Flash reports 43 species and the shared set is 43, so every species in that box is one GLM-Flash also reported.

Plotted medians and tests. All nine brackets are n.s.

| Comparison | *n* | GLM-Flash median | DeepSeek-Flash median | DeepSeek-Pro median | Pair | *U* | Raw *P* | Holm *P* |
|---|---:|---:|---:|---:|---|---:|---:|---:|
| 16S genus, Detailed | 216 | −0.0494 | −0.0517 | −0.202 | GLM-Flash vs DeepSeek-Flash | 22,969 | 0.782 | 0.782 |
| 16S genus, Detailed | 216 | −0.0494 | −0.0517 | −0.202 | GLM-Flash vs DeepSeek-Pro | 24,568 | 0.339 | 0.679 |
| 16S genus, Detailed | 216 | −0.0494 | −0.0517 | −0.202 | DeepSeek-Flash vs DeepSeek-Pro | 25,531 | 0.0896 | 0.269 |
| 16S genus, Medium | 332 | −0.0923 | −0.153 | −0.0452 | GLM-Flash vs DeepSeek-Flash | 56,555 | 0.559 | 1 |
| 16S genus, Medium | 332 | −0.0923 | −0.153 | −0.0452 | GLM-Flash vs DeepSeek-Pro | 55,695 | 0.814 | 1 |
| 16S genus, Medium | 332 | −0.0923 | −0.153 | −0.0452 | DeepSeek-Flash vs DeepSeek-Pro | 54,342 | 0.756 | 1 |
| Shotgun species, Detailed | 43 | 0.156 | −0.382 | −1.053 | GLM-Flash vs DeepSeek-Flash | 960 | 0.762 | 0.762 |
| Shotgun species, Detailed | 43 | 0.156 | −0.382 | −1.053 | GLM-Flash vs DeepSeek-Pro | 1,050 | 0.280 | 0.561 |
| Shotgun species, Detailed | 43 | 0.156 | −0.382 | −1.053 | DeepSeek-Flash vs DeepSeek-Pro | 1,103 | 0.124 | 0.373 |

DeepSeek-Pro’s shotgun Detailed median (−1.053) is the lowest of the three, and its 16S Detailed median (−0.202) is lower than the other two models’ medians near −0.05. Neither separation remains after Holm adjustment.

---

## Prompt granularity within one model

`by_prompt_models.png`. Each test compares prompts inside one model. Shannon *n* = 60 and weighted UniFrac *n* = 1,770 in every row.

### 16S Shannon and weighted UniFrac

All 18 within-model tests (three models, Shannon and weighted UniFrac, three prompt pairs) have Holm-adjusted *P* = 1.

Shannon medians:

| Model | Detailed | Medium | Simple |
|---|---:|---:|---:|
| DeepSeek-Pro | 9.825 | 9.825 | 9.832 |
| DeepSeek-Flash | 9.830 | 9.827 | 9.807 |
| GLM-Flash | 9.586 | 9.828 | 9.831 |

Weighted UniFrac medians:

| Model | Detailed | Medium | Simple |
|---|---:|---:|---:|
| DeepSeek-Pro | 0.301 | 0.301 | 0.301 |
| DeepSeek-Flash | 0.301 | 0.301 | 0.302 |
| GLM-Flash | 0.303 | 0.301 | 0.301 |

### 16S genus relative abundance

| Model | *n* | Detailed median | Medium median | Simple median | Pair | *U* | Raw *P* | Holm *P* | Bracket |
|---|---:|---:|---:|---:|---|---:|---:|---:|---|
| DeepSeek-Pro | 22 | 0.285 | 0.220 | 0.433 | Detailed vs Medium | 338 | 0.0250 | 0.0250 | \* |
| DeepSeek-Pro | 22 | 0.285 | 0.220 | 0.433 | Detailed vs Simple | 115 | 0.00298 | 0.00597 | \*\* |
| DeepSeek-Pro | 22 | 0.285 | 0.220 | 0.433 | Medium vs Simple | 55 | 1.20×10⁻⁵ | 3.60×10⁻⁵ | \*\*\* |
| DeepSeek-Flash | 32 | 0.209 | 0.297 | 0.336 | Detailed vs Medium | 354 | 0.0344 | 0.0689 | n.s. |
| DeepSeek-Flash | 32 | 0.209 | 0.297 | 0.336 | Detailed vs Simple | 308 | 0.00629 | 0.0189 | \* |
| DeepSeek-Flash | 32 | 0.209 | 0.297 | 0.336 | Medium vs Simple | 470.5 | 0.582 | 0.582 | n.s. |
| GLM-Flash | 50 | 0.197 | 0.191 | 0.190 | Detailed vs Medium | 1,293 | 0.770 | 1 | n.s. |
| GLM-Flash | 50 | 0.197 | 0.191 | 0.190 | Detailed vs Simple | 1,321 | 0.627 | 1 | n.s. |
| GLM-Flash | 50 | 0.197 | 0.191 | 0.190 | Medium vs Simple | 1,292 | 0.775 | 1 | n.s. |

DeepSeek-Pro’s three prompt distributions are separated: Medium is the low median (0.220) and Simple is the high median (0.433). DeepSeek-Flash’s Detailed median (0.209) is separated from Simple (0.336); Detailed vs Medium does not pass Holm adjustment, and Medium vs Simple is n.s. GLM-Flash’s three medians stay between 0.190 and 0.197, and all three brackets are n.s.

### Shotgun species relative abundance

| Model | *n* | Detailed median | Medium median | Simple median | Pair | *U* | Raw *P* | Holm *P* | Bracket |
|---|---:|---:|---:|---:|---|---:|---:|---:|---|
| DeepSeek-Pro | 107 | 0.190 | 0.190 | 0.190 | Detailed vs Medium | 5,729 | 0.993 | 1 | n.s. |
| DeepSeek-Pro | 107 | 0.190 | 0.190 | 0.190 | Detailed vs Simple | 5,729 | 0.993 | 1 | n.s. |
| DeepSeek-Pro | 107 | 0.190 | 0.190 | 0.190 | Medium vs Simple | 5,731.5 | 0.989 | 1 | n.s. |
| DeepSeek-Flash | 66 | 0.323 | 0.177 | 0.166 | Detailed vs Medium | 3,788 | 2.39×10⁻¹³ | 7.16×10⁻¹³ | \*\*\* |
| DeepSeek-Flash | 66 | 0.323 | 0.177 | 0.166 | Detailed vs Simple | 3,512 | 1.29×10⁻⁹ | 2.57×10⁻⁹ | \*\*\* |
| DeepSeek-Flash | 66 | 0.323 | 0.177 | 0.166 | Medium vs Simple | 1,801 | 0.0866 | 0.0866 | n.s. |
| GLM-Flash | 12 | 0.114 | 0.406 | 0.405 | Detailed vs Medium | 12 | 5.92×10⁻⁴ | 1.18×10⁻³ | \*\* |
| GLM-Flash | 12 | 0.114 | 0.406 | 0.405 | Detailed vs Simple | 9 | 3.08×10⁻⁴ | 9.24×10⁻⁴ | \*\*\* |
| GLM-Flash | 12 | 0.114 | 0.406 | 0.405 | Medium vs Simple | 73 | 0.977 | 0.977 | n.s. |

DeepSeek-Pro’s three shotgun medians are 0.190. DeepSeek-Flash’s Detailed median (0.323) sits above Medium (0.177) and Simple (0.166); Medium vs Simple is n.s. GLM-Flash has 12 shared pairs: Detailed median 0.114, Medium 0.406, Simple 0.405. Detailed is separated from both other prompts; Medium vs Simple is n.s.

### Differential abundance across Detailed and Medium

`da_prompt_method_summary.tsv`. Simple is not in this table and is not a box in these two columns. Each row has one pair, so Holm *P* equals raw *P*. The *n* is the number of taxa finite in both prompts for that model.

| Analysis | Model | Method | Detailed sessions | Medium sessions | Taxa in both prompts |
|---|---|---|---|---|---|
| 16S rRNA gene, genus | DeepSeek-Pro | DESeq2 | 1/3 | 1/3 | 111 |
| 16S rRNA gene, genus | DeepSeek-Flash | DESeq2 | 2/3 | 2/3 | 668 |
| 16S rRNA gene, genus | GLM-Flash | DESeq2 | 3/3 | 1/3 | 413 |
| Shotgun metagenome, species | DeepSeek-Pro | Wilcoxon | 1/3 | 1/3 | 14 |
| Shotgun metagenome, species | DeepSeek-Flash | Mann–Whitney U | 1/3 | 1/3 | 39 |
| Shotgun metagenome, species | GLM-Flash | DESeq2 | 2/3 | 1/3 | 9 |

The 16S session counts match the between-model DESeq2 table, because both use the same genus-level DESeq2 replicates. The shotgun session counts do not match that table. Here each model is held to the method it used at both prompts. DeepSeek-Pro is Wilcoxon (replicates: Detailed 2, Medium 2). DeepSeek-Flash is Mann–Whitney U (replicates: Detailed 3, Medium 3). GLM-Flash is DESeq2 (replicates: Detailed 1 and 3, Medium 2). The between-model shotgun panel instead keeps DESeq2 only, so DeepSeek-Flash there is replicates 1 and 2 and DeepSeek-Pro there is replicate 1.

16S genus, DESeq2 log2 fold change:

| Model | *n* | Detailed median | Medium median | *U* | *P* | Bracket |
|---|---:|---:|---:|---:|---:|---|
| DeepSeek-Pro | 111 | 0.309 | 0.00474 | 7,335 | 0.0141 | \* |
| DeepSeek-Flash | 668 | −0.262 | −0.366 | 230,106 | 0.321 | n.s. |
| GLM-Flash | 413 | −0.136 | −0.127 | 81,598 | 0.282 | n.s. |

DeepSeek-Pro is the only 16S row whose Detailed and Medium log2 fold-change distributions are separated. Its Detailed median is 0.309 and its Medium median is 0.00474.

Shotgun species. The y-axis label is the method for that row, and the three rows are not the same statistic.

| Model | Method | *n* | Detailed median | Medium median | *U* | *P* | Bracket |
|---|---|---:|---:|---:|---:|---:|---|
| DeepSeek-Pro | Wilcoxon | 14 | −0.0764 | 0.220 | 67 | 0.161 | n.s. |
| DeepSeek-Flash | Mann–Whitney U | 39 | 0.274 | 0.169 | 796 | 0.727 | n.s. |
| GLM-Flash | DESeq2 | 9 | 1.066 | −0.541 | 54 | 0.251 | n.s. |

All three shotgun brackets are n.s. GLM-Flash’s medians have opposite signs (1.066 and −0.541) on nine species; the test does not separate them. These nine species are the within-GLM Detailed∩Medium intersection. They are a different set from the 43 species shared by the three models on the DESeq2 Detailed panel.

---

## What these two figures support

Across models and across prompts, the 16S Shannon distributions (*n* = 60) and the weighted UniFrac distance distributions (*n* = 1,770) are not separated. Every one of those 36 brackets is n.s.

Genus and species relative-abundance distributions do separate in some panels. Between models, 16S genus separates at Detailed (GLM-Flash vs each DeepSeek model) and at Medium (DeepSeek-Pro vs each of the other two). Shotgun species separates at Medium for GLM-Flash vs DeepSeek-Flash and for DeepSeek-Flash vs DeepSeek-Pro, and at Simple for DeepSeek-Pro vs each of the other two. Within models, DeepSeek-Pro 16S genus separates on all three prompt pairs. DeepSeek-Flash 16S genus separates for Detailed vs Simple only. DeepSeek-Flash shotgun species separates for Detailed vs Medium and Detailed vs Simple. GLM-Flash shotgun species separates for Detailed vs Medium and Detailed vs Simple. GLM-Flash’s 16S genus prompt comparison and DeepSeek-Pro’s shotgun species prompt comparison stay n.s. on every pair. 16S genus at Simple, and shotgun species at Detailed, also stay n.s. for every between-model pair.

Where all three models ran DESeq2, the log2 fold-change distributions are not separated: 216 genera at Detailed, 332 genera at Medium, and 43 species at shotgun Detailed. Within a model, Detailed vs Medium separates only DeepSeek-Pro’s 16S DESeq2 comparison (111 genera, *P* = 0.0141). The other five within-model differential-abundance comparisons are n.s., including all three shotgun comparisons, whose methods and taxon counts differ by model (14, 39, and 9).

Task completion is 3/3 everywhere except GLM-Flash Detailed shotgun taxonomy and shotgun differential abundance (2/3, replicate 2).

*n* = 3 sessions is the repeat count. A 3/3 cell means all three runs produced a usable numeric artifact. It does not by itself show that the model is insensitive to a new run. The abundance and fold-change *P* values inherit the pseudoreplication described above.

Concordance summaries that are not in these two figures (ICC, Mantel, Procrustes, PERMANOVA) are not reported here.

---

## Protocol

These notes record how the experiment is run. Each replicate is a new OpenClaw conversation.

### Question

Does MicroBioAgent finish the same Case 1 analysis under variation of **model** and **prompt granularity**, and do the 16S α/β diversity products stay consistent across repeats?

Robustness is **orthogonal** to ablation: the full system (patched OpenClaw, plugin skills, `CODING.md`) stays on. Only the user prompt and the LLM change.

### Design

**Matrix:** 3 models × 3 prompt granularities × 3 independent runs = 27 sessions.

| Factor | Levels | What is held fixed |
|--------|--------|--------------------|
| LLM | three models (names recorded per run) | prompt, workspace, skills, patch, data |
| Prompt | detailed / medium / simple | model (when scoring that axis), data, system |
| Repeat | 3 new conversations | same model + same prompt file |

Do not cross this matrix with ablation conditions. Do not continue a previous session. Do not reuse a previous `job_id`.

### Task (same scientific goal in every cell)

Rhizosphere **16S** and matched **shotgun** from a tomato wilt experiment: **4 cultivars × 3 timepoints × 3 biological replicates** in the prompt statement. Cultivars: A57 (susceptible control), HG70 (susceptible male parent), HG64 (resistant female parent), HF12 (resistant F1). Shared resistance markers are defined on **HG64** and **HF12** at **T1**, **T2C**, and **T2**.

The three prompts differ **only** in how much method is specified:

| Prompt | What the agent is told |
|--------|------------------------|
| `prompt_detailed.md` | SOP: Shannon; weighted / unweighted UniFrac and Bray–Curtis; weighted-UniFrac PCoA; PERMANOVA + PERMDISP; taxonomy + DA; UpSet of shared HG64∩HF12 markers; the same DA on shotgun species. |
| `prompt_medium.md` | The same analysis **goals** (characterize data; 16S diversity / taxonomy / DA; shotgun taxonomy / DA; shared markers at T1/T2C/T2). Metrics, tests, and figure types are left to the agent. |
| `prompt_simple.md` | Two sentences: analyze the 16S + shotgun wilt experiment and identify microbiome patterns associated with resistance. |

Prompts list **tasks**, not file paths. Data reach the agent by copying `robustness/stage/` into that session’s job `stage/`.

### Frozen inputs

Upstream compute that is **not** the robustness question is frozen so repeats measure the agent, not DADA2 or KneadData noise.

**16S** (`stage/16s/`): post-DADA2 ASV table (`.qza` / `.tsv`), representative sequences, rooted tree, DADA2 stats, sample metadata, amplicon sample table. Do not re-import FASTQ, re-run DADA2, or rebuild the tree.

**Shotgun** (`stage/shotgun/`): metadata plus paired FASTQ in `reads/` — KneadData-cleaned libraries randomly subsampled to **20%** of reads (`seqtk`, seed 42; 36 libraries). Do not re-run KneadData.

**Off-limits:** precomputed diversity / PERMANOVA / figures under `PRJNA777724/qiime2_16s_outputs/diversity/` (except the frozen rooted tree), existing MetaPhlAn tables, KneadData directories, raw FASTQ, and project helper scripts. Reuse of those products would make repeated runs look identical for the wrong reason.

The 16S metadata already carries corrected HG64 T2/T2C labels. 16S also includes T3/T3C; shotgun does not. Prompts keep the original “3 timepoints” wording for the shared-marker task (T1, T2C, T2).

### Run procedure

1. Install the **full** MicroBioAgent workspace (`AGENTS.md`, `TOOLS.md`, `CODING.md`, `IDENTITY.md`, `registry/`) and the **patched** OpenClaw gateway. Load plugin skills.
2. Copy `robustness/stage/` into a **new** session job `stage/` (or equivalent bind). Do not point the agent at the original `PRJNA777724/` analysis tree.
3. Paste **one** of the three prompts as the user message. Confirm the plan if the agent asks; then do not coach methods.
4. After the session ends (or is marked blocked), archive `job_id`, model id, prompt file, transcript, and `analysis/`.
5. Repeat until the 3 × 3 × 3 matrix is filled (27 sessions in total).

Zero intervention except safety / disk failure. A hang or timeout is a failed replicate; record the last finished step.

### Scoring

Primary: **task completion** on a rubric aligned to the detailed prompt’s sections (data characterization; 16S α; 16S β; 16S taxonomy/DA; shotgun taxonomy/DA). Each item 0 / 0.5 / 1 by whether the required artifact exists and is usable — not by fluent chat. The heatmaps in the results section use a later pass/fail of that idea: a task is complete when a numeric result exists.

Secondary items listed for the same runs, and not computed in the two figures above: Shannon correlation and an agreement summary across the three repeats of a cell (any ICC estimate is exploratory because each cell has only three runs); Mantel tests on the distance matrices the run actually produced; Procrustes on ordinations (raw PCoA coordinates are not compared); and the discrete choices of rarefaction depth, metrics, and PERMANOVA formula.

Also record protocol adherence (did a detailed-prompt run use Shannon and the three β metrics?) so a complete but method-wrong job is not scored as a scientific success.

*n* = 3 is an initial repeatability screen. Report the individual runs and rates with intervals; do not treat a 3/3 cell as proof that the model is insensitive.
