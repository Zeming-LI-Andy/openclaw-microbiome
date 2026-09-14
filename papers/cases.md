# Case-study cards

Fill from the cloud jobs. Empty fields stay `TBD` in the manuscript.
Do not invent accessions, *n*, wall times, or tool versions.

## Case 1 — Tomato rhizosphere / bacterial-wilt resistance

| Field | Value |
|-------|--------|
| Working title | Heritability of tomato rhizosphere communities and resistance to *Ralstonia* |
| Role in paper | 16S end-to-end + MetaPhlAn (amplicon ↔ reference-based taxonomy) |
| Data type | 16S amplicon; shotgun for MetaPhlAn |
| *n* samples / groups | TBD |
| Phenotype / design | Resistance to bacterial wilt; host genotype / heritability TBD |
| Public accession | TBD |
| Server `job_id` / path | TBD |
| Skills used | 16S: TBD. Shotgun: MetaPhlAn (+ KneadData?). Stats: TBD |
| Skills skipped and why | TBD |
| Human interventions | TBD |
| Wall time | TBD |
| Key artifacts (for Fig. 3) | TBD |
| What we will *not* claim | A new plant-breeding genetic mechanism |

## Case 2 — CRC case–control

| Field | Value |
|-------|--------|
| Working title | Colorectal cancer case–control: composition, function, classifier |
| Role in paper | Reference-based shotgun + HUMAnN + study-specific classifier |
| Data type | Shotgun metagenomes |
| *n* case / control | TBD |
| Public accession | TBD |
| Server `job_id` / path | TBD |
| Skills used | MetaPhlAn, HUMAnN, stats / custom classifier in `mgx-base` |
| Classifier | Algorithm, features, CV: TBD (take from the job) |
| Skills skipped and why | TBD |
| Human interventions | TBD |
| Wall time | TBD |
| Key artifacts (for Fig. 4) | TBD |
| What we will *not* claim | A new CRC diagnostic biomarker |

## Case 3 — MAG recovery + composition + metabolic potential

| Field | Value |
|-------|--------|
| Working title | MAG recovery, community composition, and metabolic potential |
| Role in paper | Assembly-based / de novo arm |
| Data type | Shotgun (short-read / hybrid: TBD) |
| *n* samples | TBD |
| Public accession | TBD |
| Server `job_id` / path | TBD |
| Aviary stages run | assemble / recover / annotate / cluster: TBD |
| Composition source | MAG abundance and/or profiler: TBD |
| Metabolism tools actually run | gapseq / EggNOG / Bakta / gutSMASH / antiSMASH: TBD |
| Skills skipped and why | TBD |
| Human interventions | TBD |
| Wall time | TBD |
| Key artifacts (for Fig. 5) | TBD |
| What we will *not* claim | A new MAG binner or assembler |

## Robustness and ablation (later)

| Experiment | Protocol (freeze before scoring) | Metric | Server path |
|------------|----------------------------------|--------|-------------|
| Prompt paraphrase | TBD | Completion + artifact check | TBD |
| Repeat trials | TBD | Success / fail | TBD |
| Session resume | TBD | Continues after exec wake | TBD |
| Ablation: no skills | TBD | TBD | TBD |
| Ablation: no plan | TBD | TBD | TBD |
| Ablation: no session job | TBD | TBD | TBD |
| Ablation: no exec wake | TBD | TBD | TBD |
| Ablation: no registries | TBD | TBD | TBD |
