# Case study 3 — colorectal-cancer faecal metagenomes

Cohort: 128 faecal metagenomes, 74 colorectal cancer (CRC; 36 early, stages I–II; 38 late, stages III–IV) and 54 controls. Species profiles are MetaPhlAn relative abundances. Functional panels use HUMAnN gene-family and KEGG Orthology (KO) abundances.

Figure: `case_studies/case_study_3/20260904-121722-user-requested-job-setup-f828dd01/.cursor/Case-study-3-Fig_composite.png` (Fig1_crc_case_study).

## Species-level beta diversity

Bray–Curtis PCoA did not separate controls, early CRC and late CRC into discrete clusters (PC1 11.3%, PC2 9.2%). PERMANOVA nevertheless detected a community difference by CRC status (F = 2.32, P = 0.002, n = 128) and by disease stage (F = 1.65, P = 0.009). Sex (P = 0.88), age (P = 0.13) and BMI (P = 0.31; n = 127) were not significant.

## Differential species and co-occurrence

Wilcoxon tests with Benjamini–Hochberg correction gave 8 CRC-enriched and 2 control-enriched species at q < 0.05. Among the labelled taxa, *Parvimonas micra* (q = 4 × 10⁻⁶), *Peptostreptococcus stomatis* (q = 5 × 10⁻⁵), *Fusobacterium nucleatum* (q = 0.003) and *Solobacterium moorei* (q = 0.020) were CRC-enriched. *Eubacterium ventriosum* was control-enriched (q = 0.015).

The Spearman network of the ten species with q < 0.05 contained 16 positive edges (|ρ| ≥ 0.4, BH q < 0.05). *P. micra* was the highest-degree hub. Annotated edges were *P. micra*–*F. nucleatum* (ρ = 0.49) and *P. micra*–*S. moorei* (ρ = 0.53). *E. ventriosum* and *F. saccharivorans* had no edges at this threshold.

## Functional marker panels

mRMR selected 15-feature logistic-regression panels from gene-family and KO abundances. In nested 5-fold cross-validation, the gene-family panel had a pooled AUROC of 0.902 (outer-fold AUROCs 0.86–0.96; Youden sensitivity 0.82, specificity 0.89). The KO panel had a pooled AUROC of 0.632 (outer-fold AUROCs 0.59–0.72; Youden sensitivity 0.41, specificity 0.87). Most selected coefficients were positive (higher abundance in CRC) in both panels.
