# Case study 4 — MAG recovery, composition and metabolic gene counts in LMWPE, C30 and C40 enrichments

**Job:** `20260902-131309-new-analysis-job-aef3bea3`  
**Manuscript role:** Case 3 (assembly-based MAG recovery, CoverM composition, eggNOG annotation).  
**Source study:** Sandholm et al., *ISME J* (2025).  
**Figure:** `Fig_composite.png`  
**Design:** Six shotgun metagenomes from two soil inocula (S1, S2) grown on LMWPE, C30 or C40. HQ: completeness ≥ 90% and contamination < 5%; MQ: completeness ≥ 50% and contamination < 10%. Taxonomy: GTDB R232 (*Pseudomonas* placed in *Aquipseudomonas*). Panel **d** counts predicted CDS that match module rules in one representative MAG per focal taxon, not unique KO types and not transcript abundance.

These notes summarize only the specified composite figure. They do not claim a new binner or a complete reproduction of the source MAG census.

---

## Fig. 1 (composite) | MAG recovery, taxonomic composition and annotated gene counts

Across six enrichments, 151 HQ or MQ MAGs were recovered (101 HQ, 50 MQ). Dereplication at 95% ANI retained 73 representatives (42 HQ, 31 MQ). Per-sample recovered (HQ + MQ) and ANI 95% counts were:

| Enrichment | Recovered HQ / MQ | ANI 95% HQ / MQ |
|------------|-------------------|-----------------|
| S1 LMWPE | 15 / 4 (19) | 2 / 3 (5) |
| S1 C30 | 18 / 8 (26) | 16 / 8 (24) |
| S1 C40 | 11 / 6 (17) | 2 / 1 (3) |
| S2 LMWPE | 17 / 10 (27) | 5 / 4 (9) |
| S2 C30 | 23 / 14 (37) | 14 / 13 (27) |
| S2 C40 | 17 / 8 (25) | 3 / 2 (5) |

Each enrichment is a single metagenome (no biological replicates).

Genus-level CoverM abundances split the cultures by inoculum and substrate. S1 LMWPE and S1 C30 were dominated by *Acinetobacter* (64% and 67%). S1 C40 and S2 LMWPE were dominated by *Aquipseudomonas* (64% and 57%). S2 C30 and S2 C40 had lower *Aquipseudomonas* fractions (29% and 30%), with *Mesorhizobium* prominent in S2 C40 (27%).

Species ranking in any sample’s top five followed the same pattern. *Acinetobacter guillouiae* was the most abundant MAG species in S1 LMWPE (64%) and S1 C30 (67%). S1 C40 was led by *Aquipseudomonas* sp002980155 (41%) and sp036884845 (22%). S2 LMWPE was led by *Aquipseudomonas* sp003050835 (42%); *A. fluorescens_BJ* was the most abundant *Aquipseudomonas* in S2 C40 (25%). Grey cells in the heatmap are species outside that sample’s top five, not proof of absence.

eggNOG annotation of one representative MAG per focal taxon gave the following CDS counts in three modules (alkane terminal oxidation; 2-ketone / oxidized-derivative degradation; β-oxidation, KEGG M00087):

| Taxon | Alkane ox. | 2-ketone / ox. deriv. | β-oxidation |
|-------|------------|------------------------|-------------|
| *A. guillouiae* (HQ) | 4 | 10 | 7 |
| *A. aquatica* (HQ) | 0 | 3 | 3 |
| *Achromobacter* sp. (HQ) | 4 | 10 | 9 |
| *A. kerstersii* (HQ) | 2 | 9 | 7 |
| *A. putida_R* (MQ) | 4 | 3 | 8 |
| *A. fluorescens_BJ* (MQ) | 5 | 11 | 5 |
| *A. veronii* (HQ) | 9 | 14 | 6 |
| *A. sp002029345* (HQ) | 4 | 17 | 10 |
| *Aquipseudomonas* sp. (HQ) | 11 | 19 | 8 |
| *K. soli* (MQ) | 0 | 6 | 0 |

Most focal MAGs carried genes in all three modules. *A. aquatica* lacked alkane-initiation markers. *K. soli* lacked alkane terminal-oxidation and M00087 β-oxidation genes. These integers are genomic CDS counts, not expression.
