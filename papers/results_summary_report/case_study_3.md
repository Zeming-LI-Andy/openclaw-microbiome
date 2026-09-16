# Case study 3 — CRC faecal metagenomes (species beta diversity, markers, functional classification)

**Job:** `20260904-121722-user-requested-job-setup-f828dd01`  
**Manuscript role:** Case 2 (reference-based shotgun: MetaPhlAn + HUMAnN + classifier).  
**Source study:** Yu et al., *Gut* (2017) 66:70–78 (China discovery cohort C1).  
**Figure:** `Fig1_crc_case_study.png`  
**Design:** 128 faecal metagenomes; 74 CRC (36 stages I–II, 38 stages III–IV) and 54 controls. Species relative abundances from MetaPhlAn; gene-family and KO abundances from HUMAnN3.

These notes summarize only the specified six-panel figure. They do not claim a new CRC diagnostic marker.

---

## Fig. 1 | Species-level beta diversity, marker taxa and functional classification

Species-level Bray–Curtis distances differed by disease status and stage. PERMANOVA gave *P* = 0.002 for CRC versus control (*F* = 2.32) and *P* = 0.009 for disease stage (*F* = 1.65). Sex (*P* = 0.88), age (*P* = 0.13) and BMI (*P* = 0.31; 127 of 128 samples) were not significant. PCoA (PC1 11.3%, PC2 9.2%) showed overlapping clouds with a shift of CRC samples relative to controls; early and late CRC were not fully separated.

Wilcoxon rank-sum tests (CRC versus control, Benjamini–Hochberg) identified ten species at *q* < 0.05 (eight CRC-enriched, two control-enriched). The five taxa emphasized in the source study were recovered in the same direction: *Parvimonas micra* (*q* = 4 × 10⁻⁶), *Peptostreptococcus stomatis* (*q* = 5 × 10⁻⁵), *Fusobacterium nucleatum* (*q* = 0.003), *Solobacterium moorei* (*q* = 0.020) and control-enriched *Eubacterium ventriosum* (*q* = 0.015).

Among those ten species, Spearman co-occurrence yielded 16 positive edges (|ρ| ≥ 0.4, BH *q* < 0.05). *P. micra* was the highest-degree hub (degree = 6). Annotated edges included *P. micra*–*S. moorei* (ρ = 0.53) and *P. micra*–*F. nucleatum* (ρ = 0.49), forming an oral-pathogen cluster with *P. stomatis*, *Dialister pneumosintes*, *Gemella morbillorum* and *F. nucleatum*. *E. ventriosum* and *Faecalibacterium saccharivorans* were isolated (degree 0). The *F. nucleatum*–*S. moorei* edge was not retained at this threshold (ρ = 0.375 in the underlying matrix).

From 841,261 gene families (38,124 with *q* < 0.05) and 4,407 KOs (22 with *q* < 0.05), 15-feature mRMR panels were trained as L2-regularized logistic regression. Nested fivefold cross-validation gave pooled AUROC = 0.864 for the gene-family panel and 0.714 for the KO panel. Outer-fold AUROC ranges shown on the figure were 0.81–1.00 (gene families) and 0.65–0.79 (KOs). These values describe discrimination on this cohort under nested CV; they are not an external validation of the source study’s qPCR gene markers.
