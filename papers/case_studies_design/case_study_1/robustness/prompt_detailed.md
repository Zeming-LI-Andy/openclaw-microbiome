You are provided with rhizosphere shotgun metagenomic data and matched 16S rRNA gene amplicon data from a tomato bacterial-wilt experiment.
Conduct a comprehensive exploratory and comparative microbiome analysis covering both 16S rRNA and shotgun metagenomic profiling.

## Data Characterization and Quality Control

- Describe all available metadata variables and the hierarchical structure of the dataset: cultivar genotype, resistance phenotype, sampling timepoint, inoculation treatment, biological replicate.
- Visualize the experimental design, sequencing depth, and QC retention using sample-flow diagrams and distribution plots stratified by cultivar, timepoint, and treatment.

## 16S rRNA Alpha Diversity Analysis

- Calculate Shannon diversity for each sample from the post-QC, non-chimeric ASV feature table after sequencing-depth normalization.
- At each sampling timepoint, compare Shannon diversity among cultivars and between resistant and susceptible phenotype groups.
- Visualize Shannon diversity with box/violin plots by cultivar and resistance phenotype, faceted by timepoint and treatment.

## 16S rRNA Beta Diversity Analysis

- Quantify between-sample dissimilarity from the post-QC ASV feature table using **Weighted UniFrac**, **Unweighted UniFrac**, and **Bray–Curtis**.
- Visualize weighted-UniFrac PCoA with samples colored by phenotype and shaped or faceted by cultivar, timepoint, and treatment.
- Use PERMANOVA to assess resistance phenotype, cultivar, inoculation treatment, sampling timepoint, and prespecified interaction terms. Assess homogeneity of multivariate dispersion with PERMDISP before interpreting PERMANOVA.

## 16S Taxonomic Profiling and Differential Abundance Analysis

- Conduct taxonomic classification and abundance-composition analysis.
- At each independent sampling timepoint, identify taxa with significantly different abundances between each resistant focal cultivar and the susceptible control group.
- Screen and summarize microbial markers significantly enriched in both resistant cultivars **HG64** and **HF12** at **T1**, **T2C**, and **T2**. Define these shared taxa as core resistance-associated biomarkers.
- Visualize composition with stacked bar plots and differential taxa with volcano plots or heatmaps; summarize shared biomarkers with an UpSet plot.

## Shotgun Metagenome Taxonomic and Differential Abundance Analysis

- Perform species-level taxonomic annotation and abundance profiling.
- At each independent sampling timepoint, identify taxa with significantly different abundances between each resistant focal cultivar and the susceptible control group.
- Screen and summarize markers significantly enriched in both **HG64** and **HF12** at **T1**, **T2C**, and **T2** as core resistance-associated biomarkers.
- Visualize species-level composition with stacked bar plots and differential species with volcano plots or heatmaps; summarize shared markers with an UpSet plot.
