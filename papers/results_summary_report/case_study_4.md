# Case study 4 — LMWPE, C30 and C40 enrichment cultures

Six metagenomes from two inocula (S1, S2), each grown on LMWPE, C30 or C40. Each enrichment is one metagenome. High-quality (HQ) and medium-quality (MQ) MAGs were counted before and after ANI 95% dereplication. Taxonomy is GTDB R232, which places the former *Pseudomonas* MAGs in *Aquipseudomonas*. Panel d counts genes annotated by eggNOG to each module in one representative MAG per focal taxon. The number is the count of annotated genes (copies), not the number of distinct functional types, and not transcript abundance.

Figure: `case_studies/case_study_4/20260902-131309-new-analysis-job-aef3bea3/.cursor/nature/Case-study-4-Fig_composite.png` (Fig_composite).

## MAG recovery

Assembly and binning recovered 153 HQ/MQ MAGs (100 HQ, 53 MQ). ANI 95% dereplication retained 75 representatives (50 HQ, 25 MQ).

| Enrichment | Recovered HQ / MQ | ANI 95% HQ / MQ |
|---|---|---|
| S1 LMWPE | 15 / 4 | 9 / 3 |
| S1 C30 | 18 / 9 | 9 / 4 |
| S1 C40 | 11 / 6 | 4 / 2 |
| S2 LMWPE | 17 / 11 | 8 / 4 |
| S2 C30 | 22 / 15 | 13 / 9 |
| S2 C40 | 17 / 8 | 7 / 3 |

S2 C30 yielded the most MAGs before and after dereplication (37 recovered, 22 representatives). S1 C40 yielded the fewest (17 recovered, 6 representatives).

## Taxonomic composition

*Acinetobacter guillouiae* dominated the two S1 short-chain enrichments: 64% of CoverM abundance in S1 LMWPE and 67% in S1 C30. S1 C40 was instead dominated by *Aquipseudomonas* (*A.* sp002980155, 42%; *A.* sp036884845, 23%).

S2 communities were not *Acinetobacter*-dominated. The most abundant MAG species were *Aquipseudomonas* sp003050835 in S2 LMWPE (42%), *Mesorhizobium* sp900116595 and *Aquipseudomonas moorei* in S2 C30 (16% each), and *Mesorhizobium* sp900116595 (27%) with *Aquipseudomonas fluorescens_BJ* (25%) in S2 C40. S2 C30 and S2 C40 also had a large unmapped fraction.

## Genes annotated to three metabolic modules

| MAG | Quality | Alkane terminal oxidation | 2-ketone / oxidized derivatives | β-oxidation (M00087) |
|---|---|---:|---:|---:|
| *A. guillouiae* | HQ | 4 | 10 | 7 |
| *A. aquatica* | HQ | 0 | 3 | 3 |
| *Achromobacter* sp. | HQ | 4 | 10 | 9 |
| *A. kerstersii* | HQ | 2 | 9 | 7 |
| *A. putida_R* | MQ | 4 | 3 | 8 |
| *A. fluorescens_BJ* | MQ | 5 | 11 | 5 |
| *A. veronii* | HQ | 9 | 14 | 6 |
| *A.* sp002029345 | HQ | 4 | 17 | 10 |
| *Aquipseudomonas* sp. | HQ | 11 | 19 | 8 |
| *K. soli* | MQ | 0 | 6 | 0 |

Eight of the ten focal MAGs had annotated genes in all three modules. *A. aquatica* had no alkane-terminal-oxidation genes (0 / 3 / 3). *K. soli* had no alkane-terminal-oxidation genes and no M00087 β-oxidation genes (0 / 6 / 0). The *Aquipseudomonas* sp. representative had the highest counts in alkane terminal oxidation (11) and 2-ketone / oxidized-derivative degradation (19).
