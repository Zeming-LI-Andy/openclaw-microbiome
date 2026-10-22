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

Brackets on both figures are pairwise two-sided Mann–Whitney U tests on the values that enter the boxes. A pair is tested only when both groups have at least five values. Every differential-abundance panel in these two figures has a bracket. Holm adjustment is inside that panel (three pairs when three groups are present; one pair when only Detailed and Medium are compared, so the Holm *P* equals the raw *P*). The Holm step-down is the usual one: sort the raw *P* values, multiply the *k*-th by the number of tests still remaining, then enforce monotonicity and cap the result at 1. Stars are Holm *P* < 0.05 (\*), < 0.01 (\*\*), < 0.001 (\*\*\*); otherwise the bracket is n.s. These brackets compare distributions of reported values. Samples, sample pairs, taxa, and contrasts come from one experiment and are not independent replicates. A bracket is not a new biological differential-abundance test. The boxes hide points beyond the whiskers. The test and the reported median use every value, including those hidden points.

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

Genus candidates are text tables whose path contains `genus` and does not contain shotgun, MetaPhlAn, or species. Species candidates contain `species` or `merged_abundance` and do not contain `16s` or `genus`. Pathway, phylum, class, order, and family tables are not candidates. A differential-abundance path is not a candidate unless the filename is a species abundance table: it contains both `metaphlan` and `species`, contains `species_samples`, or starts with `species_relab`. Significance, result, p-value, LEfSe, MaAsLin, DESeq, and ANCOM files stay out. Other candidates have to look like an abundance table (`relab`, `relative`, `composition`, `count`, `proportion`, or `genus_table`). Those species-abundance filenames are accepted without that extra token.

The table is turned so that rows are samples. A trailing `_profile` is removed first, so a MetaPhlAn column such as `HG70RS3T2_profile` is read as the sample id. A sample id is recognized only when it matches a cultivar–timepoint–replicate pattern such as `A57-T1-RS1`. At least 30 samples are required. Genus and species names are taken from a `g__` or `s__` label when that label is present, otherwise from the last taxonomy token. The name is lowercased and spaces become underscores. Blank names, `unclassified`, `uncultured`, `incertae_sedis`, and species labels that end in `_sp` or are shorter than five characters are dropped. Strain labels (`t__`) are not species. Duplicate taxon columns are summed. Duplicate sample rows keep the first.

A merged table is converted before taxon names are filtered. Non-numeric cells become 0 and negative values are clipped to 0. If the table contains species rows and also a higher rank or `UNKNOWN`, only the species rows are kept before the scale is chosen. Kingdom through genus repeat the same reads. The whole table is classified once. If the median row sum is at most 1.5, the table is already relative abundance and its values are kept. If the maximum is at most 100 and the median row sum is between 50 and 150, it is a percentage table and is divided by 100. Any other large-sum table is raw counts: each sample is divided by its own row total, including taxa that the name filter will drop. Names are filtered after that conversion. Blank names, and the other names dropped above, leave the table, and the remaining values are not scaled to 1. Zero abundances are dropped.

A single-sample file is handled on its own. MetaPhlAn `*_profile.txt` files are the single-sample species source. Each file is one sample. The `UNKNOWN` line is ignored when reading the file's scale, because that line is sometimes a percentage while the clade lines are proportions. A file whose clade values exceed 1.5 and stay at most 100 is divided by 100. A file whose clade values stay at most 1.5 is kept as stored. A file whose clade values exceed 100 is treated as counts and each species is divided by the sum of the species rows in that file. Species that fail the name filter are removed after this conversion, without a second scaling. Files are then placed side by side. Counts from different samples are not added into one denominator.

If no genus table passes, ASV counts are collapsed with a taxonomy table, or a 16S BIOM whose observations already carry `g__` labels is collapsed. Each genus is divided by the full sample total, including reads without a genus name, and is not scaled again after unnamed reads are left out. If no species table passes, the MetaPhlAn profiles above are merged. At least 30 profiles are required.

The chosen genus table is the one whose sample count is closest to 60; the chosen species table is the one closest to 36. Ties go to the table with more taxa.

Sessions of one group are then averaged per sample–taxon pair. If a session has the sample but not the taxon, that taxon contributes 0 to the average. This zero-fill is used only for composition. A pair whose average is 0 is dropped. Each group is then restricted to pairs whose session-mean relative abundance is at least 0.05. The box keeps pairs that still pass that floor in every group being compared, so the logarithmic axis has no non-positive values.

In the between-model panel the groups are the three models inside one prompt. In the between-prompt panel the groups are Detailed, Medium, and Simple inside one model. The two intersections are different sets, so the *n* of a composition box is not transferable from one figure to the other.

### Differential-abundance values

A recorded contrast is one taxon, one resistant cultivar (HF12 or HG64), one control, and the timepoint when the table records one. The control is A57, HG70, or Sus. Sus means the pooled susceptible group, A57 and HG70. It is assigned when the table or its file name names the susceptible group or a control group, when a column records the mean of the susceptible samples, or when the direction is enriched or depleted in the resistant cultivar and the comparison itself is only that cultivar. A phenotype table with no cultivar and no timepoint is one contrast, resistant versus susceptible. The sign of the log2 fold change is the direction of that contrast.

A plotted point is one taxon, one resistant cultivar, and one timepoint, for example `Abditibacterium|HF12_T1`. Inside one session, every susceptible control for that point is averaged. A57, HG70, and Sus in the same session become one number. GLM-Flash Detailed replicate 1 stores `lfc_vs_A57` and `lfc_vs_HG70` on the same row; those two log2 fold changes are averaged before the session mean. A session with only one control contributes that log2 fold change unchanged. Sessions of the same model and prompt are then averaged on this point. A session that did not report the point is left out of the mean. It is not filled with zero.

A point enters a between-model box when it is present for all three models, and a between-prompt box when it is present at both Detailed and Medium. Each box then holds one value per point, so the two sides of a bracket have the same *n*. The two intersections are different. A phenotype contrast matches only another phenotype contrast. LEfSe LDA is not a log2 fold change and does not enter these boxes. Simple is not in the prompt differential-abundance columns.

Within one table, rows that name the same taxon and the same contrast, including the same control, become their median. A table with one log2 fold-change column against A57 and another against HG70 is read as two contrasts, and those two values are then averaged into the plotted point. If a MaAsLin `model` column contains an abundance model, only those rows are kept. The compiled `daa_master.tsv` files had dropped that column; they are rebuilt from the abundance rows in `daa/<timepoint>/all_results.tsv`, so a prevalence coefficient is not combined with the abundance coefficient. Those MaAsLin tables are not part of the DESeq2, Wilcoxon, or Mann–Whitney panels in these two figures. A species result has to carry a species name. A genus label is not used in its place, and an ASV table with an empty species column is not read as a 16S genus table. A table is dropped when more than 20% of its names are hexadecimal strings of 16 or more characters.

When the same taxon and the same control occur in more than one file in a session, one value is kept. If the values differ, the larger table is kept and the two values are not averaged. GLM-Flash Detailed replicate 2 wrote genus DESeq2 results in both `16s-genus` and `16s-genus-v2`; the larger directory is the one used. The average across controls is taken after that choice.

- Model DESeq2 panels use genus-level DESeq2 for 16S and species-level DESeq2 for shotgun. A DESeq2 table is kept only when at least half of its log2 fold changes are finite. Every such table in the session is read; repeated taxon–control pairs are removed as described above, and the controls for one taxon, cultivar, and timepoint are then averaged. Shotgun Medium stays out of this panel because the three models did not share one method.
- Prompt 16S uses those same genus-level DESeq2 tables. Prompt shotgun uses the method that model produced at both prompts: DESeq2 for GLM-Flash, Mann–Whitney U for DeepSeek-Flash, and Wilcoxon for DeepSeek-Pro. Mann–Whitney and Wilcoxon tables are not held to the half-finite cutoff. Each method uses the same within-session average of controls. It does not keep only the single largest file.

Session counts in the two method tables are replicates that entered that mean, written as *n*/3. They are smaller than the completion counts wherever a finished differential-abundance run used a table that this comparison does not include.

### Why the two differential-abundance comparisons use different methods

The bracket compares distributions, so every box in one panel has to be the same kind of number. The two figures hold different factors fixed, and the runs did not produce the same tool in every cell. The method is whatever satisfies that constraint. It is not a preferred tool applied to every cell.

**Between models, prompt held fixed.** The three boxes are GLM-Flash, DeepSeek-Flash, and DeepSeek-Pro. A panel is drawn only when all three models produced the same statistic at that prompt. Genus-level DESeq2 log2 fold change meets that test for 16S Detailed and 16S Medium. Species-level DESeq2 meets it for shotgun Detailed. Those are the three panels in `case1_completion_models.png`. Shotgun Medium is omitted, and `da_model_method_summary.tsv` records “—”, because no differential-abundance tool is present in all three models at that prompt. A tool that only some sessions of a model also ran, including MaAsLin3, LEfSe, Wilcoxon, and Mann–Whitney, stays out of this panel. Putting it in would mix two statistics inside one box, or would drop a model from the comparison.

**Between prompts, model held fixed.** The two boxes are Detailed and Medium inside one model. Simple stays in the Shannon, UniFrac, and composition columns because those three products have one definition at every prompt. The differential-abundance columns are a Detailed-versus-Medium comparison, so Simple sessions are not included. The statistic has to be one that the same model produced under both prompts.

For 16S, genus-level DESeq2 meets that test in every model, so all three rows use DESeq2. An ASV-only DESeq2 table is left out, which is why DeepSeek-Flash Detailed replicate 3 counts as complete on the heatmap and does not enter the genus comparison. A table whose names are mostly long hexadecimal ASV identifiers is also dropped, so those identifiers are not treated as genus names.

For shotgun, no one tool was produced by every model under both prompts, so the row follows the tool that model did produce twice. GLM-Flash has species-level DESeq2 at Detailed (replicates 1 and 3) and at Medium (replicate 2). DeepSeek-Flash does not have shotgun DESeq2 at both prompts; the tool present at both is Mann–Whitney U (Detailed replicate 3 and Medium replicate 3). DeepSeek-Pro does not have shotgun DESeq2 at both prompts; the tool present at both is Wilcoxon (Detailed replicate 2 and Medium replicate 2). The three shotgun log2 fold changes are therefore different quantities. They stay on separate y axes and are not tested against each other. This is also why the shotgun replicates in `da_prompt_method_summary.tsv` are not the shotgun replicates in the between-model DESeq2 panel: DeepSeek-Flash’s DESeq2 replicates are 1 and 2, and DeepSeek-Pro’s DESeq2 replicate is 1.

**How several tables inside one session become one number.** Both comparisons use the contrast rule above. A file is read only when it is the assay being compared (16S or shotgun), it is not in a superseded directory, and its name does not contain `annotated`. DESeq2 is recognized by “deseq” in the path, by a `log2FoldChange` column, or by `lfcSE` together with `baseMean`, so a DESeq2 table whose name does not contain “deseq” still counts. The effect column is `log2FoldChange`, `log2FC`, `log2FC_approx`, a paired `lfc_vs_A57` or `lfc_vs_HG70` column, or a MaAsLin `coef`. A standard-error column is not an effect. Rows that name a contrast are kept when that contrast refers to resistance, phenotype, HG64, HF12, or the susceptible cultivars; a table with no contrast column keeps every row. A DESeq2 table is kept only when at least half of its log2 fold changes are finite.

- Between-model DESeq2 reads every genus or species DESeq2 table in the session. Repeated taxon–control pairs are removed as described above. The susceptible controls for one taxon, cultivar, and timepoint are then averaged, and a file is not reduced to one row per taxon before that step.
- Between-prompt DESeq2 does the same for the genus tables. It is not limited to the largest file.
- Between-prompt Mann–Whitney collects every shotgun species table with a U statistic (`U`, `statistic_U`, or `p_mwu`), skips paths marked genus or Welch, and keeps one value per taxon and control. These tables are not held to the half-finite cutoff. Controls for the same taxon, cultivar, and timepoint are then averaged.
- Between-prompt Wilcoxon collects every shotgun species table whose name marks an all-comparison or a Wilcoxon result and whose columns include a U statistic. It also keeps one value per taxon and control, then averages controls for the same taxon, cultivar, and timepoint. It is not held to the half-finite cutoff, and it is not limited to the single largest file.

Across sessions, the mean uses only the sessions listed for that method, and a point missing from one of those sessions is left missing. The between-model box then requires the taxon, cultivar, and timepoint to be present in all three models. The between-prompt box requires them at both prompts of that one model. Those are different intersections. At shotgun Detailed the three models share 228 points, one in each box. In the prompt rows both boxes contain 891 points for DeepSeek-Pro 16S, 5,108 for DeepSeek-Flash 16S, 3,984 for GLM-Flash 16S, 39 for DeepSeek-Pro shotgun, 120 for DeepSeek-Flash shotgun, and 52 for GLM-Flash shotgun.

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
| Medium | 10 | 0.454 | 0.140 | 0.158 | GLM-Flash vs DeepSeek-Flash | 95 | 7.69×10⁻⁴ | 2.31×10⁻³ | \*\* |
| Medium | 10 | 0.454 | 0.140 | 0.158 | GLM-Flash vs DeepSeek-Pro | 94 | 1.01×10⁻³ | 2.31×10⁻³ | \*\* |
| Medium | 10 | 0.454 | 0.140 | 0.158 | DeepSeek-Flash vs DeepSeek-Pro | 50 | 1 | 1 | n.s. |
| Simple | 68 | 0.158 | 0.392 | 0.392 | GLM-Flash vs DeepSeek-Flash | 899 | 7.86×10⁻¹⁰ | 2.36×10⁻⁹ | \*\*\* |
| Simple | 68 | 0.158 | 0.392 | 0.392 | GLM-Flash vs DeepSeek-Pro | 899 | 7.86×10⁻¹⁰ | 2.36×10⁻⁹ | \*\*\* |
| Simple | 68 | 0.158 | 0.392 | 0.392 | DeepSeek-Flash vs DeepSeek-Pro | 2,314 | 0.995 | 0.995 | n.s. |

At Detailed, the three species-abundance distributions are not separated. At Medium, ten shared sample–species pairs remain after the 0.05 floor. GLM-Flash’s median is 0.454. DeepSeek-Flash (0.140) and DeepSeek-Pro (0.158) are not separated from each other. At Simple, GLM-Flash’s median (0.158) sits below DeepSeek-Flash and DeepSeek-Pro, which share the median 0.392; DeepSeek-Flash vs DeepSeek-Pro is n.s.

### Why the relative-abundance distributions separate

The brackets above compare session means. A genus or species missing from a session that still has the sample is filled with 0 before that mean. The separations come from a few sessions’ annotation and table-building choices. Samples and taxa still come from one experiment.

**16S genus, Detailed.** DeepSeek-Flash replicate 1 and DeepSeek-Pro replicate 1 classified ASVs with a naive Bayes classifier trained on SILVA 138.2 V4 (515F/806R). In both taxonomies the dominant ASV `183d8dd16fc49e01dac209fb9a87f14d` (57,028 reads on A57-T2-RS1) is labeled `g__Paraherbaspirillum`, at confidence about 0.78. *Ralstonia*, *Pseudarthrobacter*, and *Sphingomonas* have no ASVs, so those genera are 0 in that session and pull the three-session mean down. The other two replicates of each model label that ASV as *Ralstonia*. This is the Detailed separation of GLM-Flash from each DeepSeek model, and DeepSeek-Flash’s Detailed-versus-Simple separation. One further DeepSeek-Flash Detailed replicate keeps only the 15 genera with the highest mean abundance, so one genus in the 32-pair intersection is absent from that table and is filled with 0. That single pair does not account for the bracket.

**16S genus, Medium.** DeepSeek-Pro replicate 2 collapsed the ASV table with `asv.groupby(labels.values)`. The taxonomy file is sorted by Feature ID and the ASV table is not, so genus labels were attached by row position. On A57-T2-RS1 the *Ralstonia* count in that table is 1,666 / 111,860 (1.49%). The same ASV joined by Feature ID is 59,200 / 111,860 (52.9%). Replicate 3 of the same model keeps the Feature-ID total. The mean of the scrambled table and the intact table is what sits below GLM-Flash (0.347) and DeepSeek-Flash (0.346). GLM-Flash versus DeepSeek-Flash stays n.s. The same Medium table is why DeepSeek-Pro’s three prompt distributions separate. DeepSeek-Pro Medium replicate 1 also trained a V4 classifier, but that genus table was not the one used here.

**Shotgun species.** GLM-Flash at Medium (all three replicates) and at Simple (replicates 1 and 2) set MetaPhlAn `--bowtie2db` to the index directory `mpa_v31_CHOCOPhlAn_201901`. The other models set `--bowtie2db` to the parent directory `/refdb/metaphlan_databases` and named the index with `--index`. With the index directory, almost no reads match a marker. GLM-Flash Medium replicate 2 turned on `--unknown_estimation` and wrote, for HG64-T1-RS1, `UNKNOWN` = 99.57% and *Stenotrophomonas acidaminiphila* = 0.254% of all reads. Replicates 1 and 3 omitted that flag, so MetaPhlAn rescaled the matched 0.43% to 100% and wrote the same species as 59.25%, in a file of about 10 species. DeepSeek-Flash and DeepSeek-Pro, on the same reads and with the parent directory, wrote about 26 species and 20.40% for this species. The Medium comparison species are inside GLM-Flash’s short list, so its median (0.454) sits above 0.140 and 0.158.

At Simple the compared species are mostly absent from those short files. On A57-T2-RS1, GLM-Flash replicate 1 wrote four species closed to 100%, led by *Streptomyces griseorubiginosus* at 53.23%, and did not write *Ralstonia*. DeepSeek-Pro replicate 1 used the same v31 index and the same reads (`SRR16817052`), with the parent directory, and wrote *Ralstonia solanacearum* at 67.83% and *Streptomyces griseorubiginosus* at 0.22%. GLM-Flash replicates 1 and 2 therefore contribute 0 for *Ralstonia*; replicate 3 contributes the 148-species table at 0.507. The three-session mean is about one third of that full table. Both DeepSeek models have the species in all three runs, and their medians are both 0.392. `--unknown_estimation` changes whether the unmatched reads are written down. The short species list follows the database directory.

GLM-Flash Detailed shotgun used the parent directory and `mpa_v30`. That is why, inside GLM-Flash, the Detailed species median sits below Medium and Simple. DeepSeek-Flash and DeepSeek-Pro shotgun prompt comparisons stay n.s.; those runs used the parent directory.

---

## DESeq2 shared across models

Lower row of panel b, with `da_model_method_summary.tsv`. A point is plotted when its taxon, cultivar, and timepoint are present for all three models. Susceptible controls inside a session have already been averaged, so each model contributes one value per point. Shotgun Medium is absent from the figure and is recorded as “—” in the table: the three models did not share one differential-abundance method at that prompt.

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

Points in each model after the within-session average of controls, before the three-model intersection, then the number that enter the box.

| Comparison | GLM-Flash before / in box | DeepSeek-Flash before / in box | DeepSeek-Pro before / in box | Points in the box |
|---|---:|---:|---:|---:|
| 16S genus, Detailed | 9,388 / 1,724 | 7,017 / 1,724 | 4,966 / 1,724 | 1,724 |
| 16S genus, Medium | 4,904 / 2,659 | 6,171 / 2,659 | 3,290 / 2,659 | 2,659 |
| Shotgun species, Detailed | 247 / 228 | 486 / 228 | 499 / 228 | 228 |

Plotted medians and tests. Each pair has the same *n* on both sides.

| Comparison | Pair | *n* | Medians | *U* | Raw *P* | Holm *P* | Bracket |
|---|---|---:|---|---:|---:|---:|---|
| 16S genus, Detailed | GLM-Flash vs DeepSeek-Flash | 1,724 | 0 vs 0.0334 | 1,466,277 | 0.498 | 0.498 | n.s. |
| 16S genus, Detailed | GLM-Flash vs DeepSeek-Pro | 1,724 | 0 vs −0.0926 | 1,527,128 | 0.160 | 0.321 | n.s. |
| 16S genus, Detailed | DeepSeek-Flash vs DeepSeek-Pro | 1,724 | 0.0334 vs −0.0926 | 1,554,332 | 0.0195 | 0.0586 | n.s. |
| 16S genus, Medium | GLM-Flash vs DeepSeek-Flash | 2,659 | 0 vs −0.0208 | 3,562,084 | 0.630 | 0.701 | n.s. |
| 16S genus, Medium | GLM-Flash vs DeepSeek-Pro | 2,659 | 0 vs −0.0375 | 3,616,219 | 0.148 | 0.443 | n.s. |
| 16S genus, Medium | DeepSeek-Flash vs DeepSeek-Pro | 2,659 | −0.0208 vs −0.0375 | 3,587,389 | 0.351 | 0.701 | n.s. |
| Shotgun species, Detailed | GLM-Flash vs DeepSeek-Flash | 228 | −0.201 vs −0.200 | 24,301 | 0.230 | 0.459 | n.s. |
| Shotgun species, Detailed | GLM-Flash vs DeepSeek-Pro | 228 | −0.201 vs −0.242 | 26,828 | 0.553 | 0.553 | n.s. |
| Shotgun species, Detailed | DeepSeek-Flash vs DeepSeek-Pro | 228 | −0.200 vs −0.242 | 28,824 | 0.0442 | 0.133 | n.s. |

All nine brackets are n.s. At 16S Detailed, DeepSeek-Flash vs DeepSeek-Pro has raw *P* = 0.0195 and Holm *P* = 0.0586. At shotgun Detailed, that same pair has raw *P* = 0.0442 and Holm *P* = 0.133. These brackets compare the reported log2 fold changes. They are not a new biological differential-abundance test.

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
| DeepSeek-Pro | 99 | 0.208 | 0.208 | 0.213 | Detailed vs Medium | 4,900.5 | 1 | 1 | n.s. |
| DeepSeek-Pro | 99 | 0.208 | 0.208 | 0.213 | Detailed vs Simple | 4,850 | 0.901 | 1 | n.s. |
| DeepSeek-Pro | 99 | 0.208 | 0.208 | 0.213 | Medium vs Simple | 4,850 | 0.901 | 1 | n.s. |
| DeepSeek-Flash | 99 | 0.219 | 0.213 | 0.213 | Detailed vs Medium | 4,785 | 0.775 | 1 | n.s. |
| DeepSeek-Flash | 99 | 0.219 | 0.213 | 0.213 | Detailed vs Simple | 4,785 | 0.775 | 1 | n.s. |
| DeepSeek-Flash | 99 | 0.219 | 0.213 | 0.213 | Medium vs Simple | 4,900 | 1 | 1 | n.s. |
| GLM-Flash | 12 | 0.114 | 0.406 | 0.405 | Detailed vs Medium | 12 | 5.92×10⁻⁴ | 1.18×10⁻³ | \*\* |
| GLM-Flash | 12 | 0.114 | 0.406 | 0.405 | Detailed vs Simple | 9 | 3.08×10⁻⁴ | 9.24×10⁻⁴ | \*\*\* |
| GLM-Flash | 12 | 0.114 | 0.406 | 0.405 | Medium vs Simple | 73 | 0.977 | 0.977 | n.s. |

DeepSeek-Pro’s three shotgun medians are 0.208, 0.208, and 0.213. DeepSeek-Flash’s are 0.219, 0.213, and 0.213. All six of those brackets are n.s. GLM-Flash has 12 shared pairs: Detailed median 0.114, Medium 0.406, Simple 0.405. Detailed is separated from both other prompts; Medium vs Simple is n.s.

### Differential abundance across Detailed and Medium

`da_prompt_method_summary.tsv`. Simple is not in this table and is not a box in these two columns. Each tested row has one pair, so Holm *P* equals raw *P*. The count is the number of taxon–cultivar–timepoint points present under both prompts. Controls inside a session are already averaged, so Detailed and Medium have the same count.

| Analysis | Model | Method | Detailed sessions | Medium sessions | Points in each box |
|---|---|---|---|---|---:|
| 16S rRNA gene, genus | DeepSeek-Pro | DESeq2 | 1/3 | 1/3 | 891 |
| 16S rRNA gene, genus | DeepSeek-Flash | DESeq2 | 2/3 | 2/3 | 5,108 |
| 16S rRNA gene, genus | GLM-Flash | DESeq2 | 3/3 | 1/3 | 3,984 |
| Shotgun metagenome, species | DeepSeek-Pro | Wilcoxon | 1/3 | 1/3 | 39 |
| Shotgun metagenome, species | DeepSeek-Flash | Mann–Whitney U | 1/3 | 1/3 | 120 |
| Shotgun metagenome, species | GLM-Flash | DESeq2 | 2/3 | 1/3 | 52 |

The 16S session counts match the between-model DESeq2 table, because both use the same genus-level DESeq2 replicates. The shotgun session counts do not match that table. Here each model is held to the method it used at both prompts. DeepSeek-Pro is Wilcoxon (replicates: Detailed 2, Medium 2). DeepSeek-Flash is Mann–Whitney U (replicates: Detailed 3, Medium 3). GLM-Flash is DESeq2 (replicates: Detailed 1 and 3, Medium 2). The between-model shotgun panel instead keeps DESeq2 only, so DeepSeek-Flash there is replicates 1 and 2 and DeepSeek-Pro there is replicate 1.

DeepSeek-Pro 16S Detailed compares HF12 or HG64 with the pooled susceptible group, and its Medium compares those cultivars with A57. DeepSeek-Pro shotgun Wilcoxon has that same split. Each session’s controls are averaged before the two prompts are compared, so a point can combine different controls. The 16S boxes contain the 891 genus–cultivar–timepoint points present under both prompts. The shotgun Wilcoxon boxes contain the 39 species–cultivar–timepoint points present under both prompts. LEfSe LDA from the other Medium replicate stays out, because it is not a log2 fold change.

16S genus, DESeq2 log2 fold change:

| Model | *n* | Detailed median | Medium median | *U* | *P* | Bracket |
|---|---:|---:|---:|---:|---:|---|
| DeepSeek-Pro | 891 | 0.0120 | 0.00474 | 403,545 | 0.543 | n.s. |
| DeepSeek-Flash | 5,108 | −0.130 | −0.144 | 13,146,380 | 0.500 | n.s. |
| GLM-Flash | 3,984 | −0.0867 | −0.00950 | 7,779,290 | 0.127 | n.s. |

None of the three 16S rows is separated.

Shotgun species. The y-axis label is the method for that row, and the three rows are not the same statistic.

| Model | Method | *n* | Detailed median | Medium median | *U* | *P* | Bracket |
|---|---|---:|---:|---:|---:|---:|---|
| DeepSeek-Pro | Wilcoxon | 39 | 0.0713 | 0.124 | 704 | 0.576 | n.s. |
| DeepSeek-Flash | Mann–Whitney U | 120 | 0.0181 | 0.508 | 6,570 | 0.242 | n.s. |
| GLM-Flash | DESeq2 | 52 | 0.883 | −1.256 | 1,637 | 0.0644 | n.s. |

None of the three shotgun rows is separated. GLM-Flash’s 52 points are the within-GLM Detailed and Medium intersection. They are a different set from the 228 points shared by the three models on the DESeq2 Detailed panel.

---

## What these two figures support

Across models and across prompts, the 16S Shannon distributions (*n* = 60) and the weighted UniFrac distance distributions (*n* = 1,770) are not separated. Every one of those 36 brackets is n.s.

Genus and species relative-abundance distributions do separate in some panels. Between models, 16S genus separates at Detailed (GLM-Flash vs each DeepSeek model) and at Medium (DeepSeek-Pro vs each of the other two). Shotgun species separates at Medium and at Simple for GLM-Flash vs each DeepSeek model. DeepSeek-Flash vs DeepSeek-Pro stays n.s. at both of those prompts. Within models, DeepSeek-Pro 16S genus separates on all three prompt pairs. DeepSeek-Flash 16S genus separates for Detailed vs Simple only. GLM-Flash shotgun species separates for Detailed vs Medium and Detailed vs Simple. GLM-Flash’s 16S genus prompt comparison, DeepSeek-Flash’s shotgun species prompt comparison, and DeepSeek-Pro’s shotgun species prompt comparison stay n.s. on every pair. 16S genus at Simple, and shotgun species at Detailed, also stay n.s. for every between-model pair. The sessions behind the abundance separations are under “Why the relative-abundance distributions separate”: a SILVA 138.2 V4 classifier, one 16S genus table collapsed by row position, and MetaPhlAn runs whose database directory was the index folder, with `--unknown_estimation` present or absent.

Where all three models ran DESeq2, each box has one value per taxon, cultivar, and timepoint, after susceptible controls inside a session are averaged. All nine brackets are n.s.: 1,724 points at 16S Detailed, 2,659 at 16S Medium, and 228 at shotgun Detailed. The closest pair is DeepSeek-Flash vs DeepSeek-Pro at 16S Detailed (raw *P* = 0.0195, Holm *P* = 0.0586). Within a model, Detailed versus Medium is n.s. in all six rows: DeepSeek-Pro 16S (891), DeepSeek-Flash 16S (5,108), GLM-Flash 16S (3,984), DeepSeek-Pro shotgun Wilcoxon (39), DeepSeek-Flash shotgun Mann–Whitney (120), and GLM-Flash shotgun DESeq2 (52).

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
