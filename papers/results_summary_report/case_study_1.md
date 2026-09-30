# Case study 1 — tomato rhizosphere after *Ralstonia* inoculation

Design: four cultivars (susceptible A57 and HG70; resistant HG64 and HF12), 16S rRNA profiles at five timepoints (T1, day 0; T2C, day 5 uninoculated; T2, day 5 inoculated; T3C, day 10 uninoculated; T3, day 10 inoculated; n = 3 per cultivar × timepoint, 60 samples), and shotgun species profiles at T1, T2C and T2 (36 samples). Genus and species enrichment tests are MaAsLin3 abundance models of each resistant cultivar against the pooled susceptible cultivars. Enrichment calls in Figs 2 and 3 use nominal P < 0.05 and a positive coefficient; they are not FDR-adjusted.

Figures:

- `case_studies/case_study_1/20260903-161334-session-job-setup-0d690772/.cursor/nature/Case-study-1-Fig1_diversity.png` (Fig1_diversity)
- `case_studies/case_study_1/20260903-161334-session-job-setup-0d690772/.cursor/nature/Case-study-1-Fig2_16s_genus_enrichment.png` (Fig2_genus_enrichment)
- `case_studies/case_study_1/20260903-161334-session-job-setup-0d690772/.cursor/nature/Case-study-1-Fig3_shotgun_species_enrichment.png` (Fig3_species_enrichment)

## Diversity and composition

Shannon diversity was high and similar across cultivars in the uninoculated samples at T1 and T3C (medians about 9.9–10.5). The resistant-versus-susceptible contrast was significant at T1 (P = 0.009) and not at T3C (P = 0.70). At T2C, HG64 was the exception (median 6.90) while the other three cultivars remained near 10; the resistant-versus-susceptible test was not significant (P = 0.18).

After inoculation, Shannon fell in the susceptible cultivars and stayed higher in the resistant cultivars. At T2, medians were 4.87 (A57), 7.17 (HG70), 10.16 (HG64) and 8.56 (HF12) (P = 0.002). At T3 they were 6.16, 5.17, 7.59 and 7.06 (P = 0.004).

Weighted UniFrac PCoA separated samples mainly by inoculation (PC1, 56.3%). Uninoculated samples clustered at negative PC1 and inoculated samples at positive PC1. PC2 (12.2%) partly separated resistant from susceptible samples, with overlap between the two phenotypes.

Genus composition was diverse at T1, T2C and T3C, with a large unclassified / incertae-sedis fraction and no single dominant genus. At T2 and T3, *Ralstonia* expanded, most strongly in the susceptible cultivars A57 and HG70.

## 16S genus enrichment

Genera enriched in both resistant cultivars (nominal P < 0.05, positive coefficient) numbered 15 (T1), 6 (T2C), 7 (T2), 8 (T3C) and 7 (T3). Cultivar-private enriched genera were more numerous at several timepoints (HG64-only / HF12-only: 13/20, 15/4, 10/19, 37/19 and 9/4).

Shared genera, in order of increasing minimum P:

- T1: *Tellurimicrobium*, *Bosea*, *Chthoniobacter*, *Emticicia*, *Candidatus* Udaeobacter, *Telluribacter*, *Sphingobacterium*, *Sphingopyxis*, *Stenotrophobacter*, *Endobacterium*, *Flavihumibacter*, an unclassified genus, *Chthonomonas*, *Luteitalea*, HT002.
- T2C: *Flaviaestuariibacter*, *Candidatus* Berkiella, MND1, *Escherichia–Shigella*, *Candidatus* Koribacter, Subgroup 10.
- T2: *Candidatus* Nitrosoarchaeum, *Aridibacter*, *Arenimicrobium*, *Stenotrophobacter*, *Aurantisolimonas*, *Tellurimicrobium*, *Hymenobacter*.
- T3C: *Devosia*, *Sphingomonas*, *Hymenobacter*, *Bacillus*, *Lactobacillus*, *Prosthecomicrobium*, *Exiguobacterium*, *Brevundimonas*.
- T3: *Pseudarthrobacter*, *Ramlibacter*, *Roseisolibacter*, *Sinomonas*, *Rossellomorea*, *Arenimonas*, *Deinococcus*.

The shared set changed with timepoint. *Tellurimicrobium* and *Stenotrophobacter* recurred at two timepoints; the other shared genera were timepoint-specific.

## Shotgun species enrichment

Species-level enrichment was sparse. The only species enriched in both HG64 and HF12 was the *Pseudomonas putida* group at T1 (HG64 coefficient 3.28, P = 0.013; HF12 coefficient 3.96, P = 0.009). Two additional species were enriched in HG64 only (*Stenotrophomonas acidaminiphila*, *Devosia riboflavina*) and one in HF12 only (*Azospirillum lipoferum*).

No species was enriched in either resistant cultivar at T2C. At T2, five species were enriched in HG64 only and two in HF12 only, with no shared species. The HG64-only set was *Ferrovibrio* sp., *Pseudomonas alcaliphila*, *Sorangium cellulosum*, *Nannocystis exedens* and *Stenotrophomonas acidaminiphila*; the HF12-only set was *Alsobacter* sp. SH9 and *Gemmatirosa kalamazoonesis*.
