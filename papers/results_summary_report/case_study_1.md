# Case study 1 — Tomato rhizosphere 16S diversity and genus enrichment

**Job:** `20260903-161334-session-job-setup-0d690772`  
**Manuscript role:** Case 1 (amplicon 16S end-to-end).  
**Source study:** Yin et al., *Microbiome* (2022) 10:227.  
**Figures:** `Fig1_diversity.png`, `Fig2_genus_enrichment.png`  
**Design:** 16S V3–V4, 60 samples (4 cultivars × 5 timepoints × 3 biological replicates). Cultivars: A57 and HG70 (susceptible), HG64 (resistant parent), HF12 (resistant F1). Timepoints: T1 (day 0), T2C (day 5, uninoculated), T2 (day 5, inoculated), T3C (day 10, uninoculated), T3 (day 10, inoculated). Shannon indices were computed on ASV tables rarefied to 56,726 reads.

These notes summarize only the two specified figures. They are demonstrations of pipeline coverage, not a standalone plant-pathology result.

The matched shotgun analysis also provides a database-version sensitivity
check for the two species emphasized by the source study.  MetaPhlAn3 detected
*Pseudomonas putida*, which was significantly enriched in resistant cultivars,
but did not resolve *Sphingopyxis unclassified*.  Reanalysis with MetaPhlAn2
detected both *P. putida* and *Sphingopyxis unclassified*, and both showed
significant between-phenotype differences.  This comparison is evidence that
the agent can execute reference-based shotgun profiling, while also showing
that recovery of a prespecified taxon depends on the reference database.  The
manuscript should report the corresponding effect sizes, statistical test,
adjusted P values, database builds, and numbers of detected samples directly
from the archived output tables before treating either association as a formal
result.

---

## Fig. 1 | Diversity and community composition across cultivar and inoculation

After inoculation with *Ralstonia*, Shannon diversity fell in all four cultivars relative to uninoculated timepoints, but the drop was larger in susceptible than in resistant plants. Mean Shannon remained near 10 at T1, T2C and T3C. At T2 it declined to 5.11 (A57), 6.82 (HG70), 6.32 (HG64) and 8.69 (HF12); at T3 it was 5.70, 5.07, 7.76 and 7.77, respectively. Two-sided Mann–Whitney tests of pooled resistant versus susceptible cultivars were significant at T1 (*P* = 0.009) and T3 (*P* = 0.004), but not at T2 (*P* = 0.24), T2C (*P* = 1.00) or T3C (*P* = 0.70). HG64 at T2 did not retain a higher Shannon index than the susceptible male parent HG70.

Weighted UniFrac PCoA separated samples primarily by inoculation on PC1 (57.2% of variance) and secondarily by resistance phenotype on PC2 (12.8%). Uninoculated samples clustered independently of sampling day; inoculated samples shifted along PC1. Resistant inoculated samples lay closer to the uninoculated centroid than did susceptible inoculated samples.

Genus-level stacked bars showed the same inoculation shift. Uninoculated communities were dominated by *Incertae sedis* and a mix of *Sphingomonas*, *Pseudarthrobacter*, *Gemmatimonas* and related genera. At T2 and T3, *Ralstonia* expanded, most strongly in A57 and HG70, concurrent with the Shannon collapse.

---

## Fig. 2 | Genera enriched in HG64 and HF12 relative to susceptible cultivars

MaAsLin 3 contrasted each resistant cultivar with pooled susceptible cultivars (A57 + HG70) within each timepoint (TSS + LOG). Volcano plots use nominal *P* = 0.05 (dashed line). Shared enrichment was defined as coefficient > 0 and *P* < 0.05 in both HG64 and HF12 at that timepoint.

Venn counts of nominally enriched genera were:

| Timepoint | HG64 only | Shared | HF12 only |
|-----------|-----------|--------|-----------|
| T1 | 17 | 14 | 22 |
| T2C | 19 | 10 | 15 |
| T2 | 7 | 4 | 27 |
| T3C | 33 | 8 | 17 |
| T3 | 10 | 7 | 4 |

Shared genera at T1 included *Candidatus* Udaeobacter, *Tellurimicrobium*, *Rhodocytophaga*, *Chthoniobacter*, *Bosea* and *Sphingopyxis*; at T2C they included *Pelagerythrobacter*, *Sphingomonas* and *Flavisolibacter*; at T2 they included *Aridibacter* and *Candidatus* Koribacter; at T3 they included *Pseudarthrobacter*, *Ramlibacter* and *Roseisolibacter*. These lists are nominal *P* intersections. After Benjamini–Hochberg correction, no genus was shared at *q* < 0.05; a single genus (*Pelagerythrobacter* at T2C) was shared at *q* < 0.1. With three replicates per cultivar, per-timepoint tests have limited power. The more stable signal in this case is therefore the inoculation-driven diversity collapse and *Ralstonia* expansion in Fig. 1, not a conserved set of FDR-significant marker genera.
