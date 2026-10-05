# Case study 3 — colorectal-cancer faecal metagenomes

Cohort: 128 faecal metagenomes, 74 colorectal cancer (CRC; 36 early, stages I–II; 38 late, stages III–IV) and 54 controls. Species profiles are MetaPhlAn relative abundances. Functional panels use HUMAnN UniRef90 gene-family abundances and KEGG Orthology (KO) abundances, where each KO is the sum of the UniRef90 RPKs mapped to it.

Figure: `case_studies/case_study_3/20260904-121722-user-requested-job-setup-f828dd01/.cursor/Case-study-3-Fig_composite.png` (Fig1_crc_case_study).

## Species-level beta diversity

Fig. 1a is classical PCoA of species-level Bray–Curtis distances; ellipses are 95% covariance ellipses. Fig. 1b shows Bray–Curtis PERMANOVA F statistics for each metadata variable. Controls, early CRC and late CRC did not form discrete clusters (PC1 11.3%, PC2 9.2%). PERMANOVA nevertheless detected a community difference by CRC status (F = 2.32, P = 0.002, n = 128) and by disease stage (F = 1.65, P = 0.009). Sex (P = 0.88), age (P = 0.13) and BMI (P = 0.31; n = 127) were not significant.

## Differential species and co-occurrence

Fig. 1c shows two-sided Wilcoxon rank-sum tests of species relative abundance (CRC versus control) with Benjamini–Hochberg q values. Eight species were CRC-enriched and two control-enriched at q < 0.05. Among the labelled taxa, *Parvimonas micra* (q = 4 × 10⁻⁶), *Peptostreptococcus stomatis* (q = 5 × 10⁻⁵), *Fusobacterium nucleatum* (q = 0.003) and *Solobacterium moorei* (q = 0.020) were CRC-enriched. *Eubacterium ventriosum* was control-enriched (q = 0.015).

Fig. 1d is the Spearman co-occurrence network of the ten species with q < 0.05. Edges require |ρ| ≥ 0.4 and BH q < 0.05; all 16 edges were positive. *P. micra* was the highest-degree hub (degree 6). Annotated edges were *P. micra*–*F. nucleatum* (ρ = 0.49) and *P. micra*–*S. moorei* (ρ = 0.53). *E. ventriosum* and *F. saccharivorans* had no edges at this threshold.

## Functional marker panels

The classifier is an L2-regularized logistic regression on standardized abundances (StandardScaler + `LogisticRegression(penalty="l2", class_weight="balanced")`). Features were selected per training fold: the 150 most significant Wilcoxon features were taken as the candidate pool, pairwise-correlation filtering removed redundancy (|ρ| > 0.8, keeping at most 30), and mRMR (maximum-relevance minimum-redundancy, Spearman-based) selected 15 features. Performance was estimated by nested 5-fold cross-validation: feature selection and tuning of C over {0.01, 0.03, 0.1, 0.3, 1.0} were done in the inner loop, and the ROC in Fig. 1f pools the outer-fold out-of-fold probabilities.

The gene-family panel had a pooled AUROC of 0.902 (outer-fold AUROCs 0.86–0.96; Youden sensitivity 0.82, specificity 0.89). The KO panel had a pooled AUROC of 0.632 (outer-fold AUROCs 0.59–0.72; Youden sensitivity 0.41, specificity 0.87). Most selected coefficients were positive (higher abundance in CRC) in both panels.
