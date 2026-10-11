You are provided with rhizosphere shotgun metagenomic data and matched 16S rRNA gene amplicon data from a tomato bacterial-wilt experiment.
Conduct a comprehensive exploratory and comparative microbiome analysis covering both 16S rRNA and shotgun metagenomic profiling, following the standardized workflow below.

## Data Characterization and Quality Control

- Systematically describe all available metadata variables and the overall hierarchical structure of the dataset, including:
 - Cultivar genotype
 - Resistance phenotype
 - Sampling timepoint
 - Inoculation treatment
 - Biological replicate information
- Visualize the experimental design, sequencing depth, and QC retention using sample-flow diagrams and distribution plots stratified by cultivar, timepoint, and treatment.

## 16S rRNA Alpha Diversity Analysis

- Alpha Diversity Calculation: Calculate the Shannon diversity index for each sample using the post-QC, non-chimeric ASV feature table after applying a predefined sequencing-depth normalization strategy.
- Stratified Group Comparisons: At each sampling timepoint, compare Shannon diversity among tomato cultivars and between resistant and susceptible phenotype groups.
- Visualize Shannon diversity with box/violin plots by cultivar and resistance phenotype, faceted by timepoint and treatment.

## 16S rRNA Beta Diversity Analysis

- Beta diversity quantification: Quantify between-sample community dissimilarity using distance matrices calculated from the post-QC ASV feature table:
  - **Weighted UniFrac:** incorporates phylogenetic relationships and taxon abundances.
  - **Unweighted UniFrac:** evaluates phylogeny-based presence/absence differences.
  - **Bray–Curtis:** primarily captures abundance-based compositional dissimilarity.

- Visualization: Visualize weighted-UniFrac PCoA with samples colored by phenotype and shaped or faceted by cultivar, timepoint, and treatment.
- Statistical testing: Use PERMANOVA to assess the effects of:
  - Resistance phenotype
  - Cultivar
  - Inoculation treatment
  - Sampling timepoint
  - Prespecified interaction terms
  - Before interpreting PERMANOVA results, assess homogeneity of multivariate dispersion using PERMDISP.

## 16S Taxonomic Profiling and Differential Abundance Analysis

- Taxonomic Composition Profiling: Conduct taxonomic classification and abundance-composition analysis for the 16S datasets.
- Group-Specific Differential Abundance Screening: At each independent sampling timepoint, identify microbial taxa with significantly different abundances between each resistant focal cultivar and the susceptible control group.
- Shared Resistance-Associated Marker Identification: Screen and summarize microbial markers significantly enriched in both resistant cultivars, **HG64** and **HF12**, at the **T1**, **T2C**, and **T2** timepoints. Define these shared taxa as core resistance-associated biomarkers.
- Visualize taxonomic composition with stacked bar plots and differential taxa with volcano plots or heatmaps; summarize shared biomarkers using an UpSet plot.

## Shotgun Metagenome Taxonomic and Differential Abundance Analysis

- Metagenomic Taxonomic Composition Analysis: Perform high-resolution, species-level taxonomic annotation and abundance profiling using shotgun metagenomic data to comprehensively characterize the rhizosphere microbial species-composition landscape across experimental groups.
- Group-Specific Differential Abundance Screening: At each independent sampling timepoint, identify microbial taxa with significantly different abundances between each resistant focal cultivar and the susceptible control group.
- Shared Resistance-Associated Marker Identification: Screen and summarize microbial markers significantly enriched in both resistant cultivars, **HG64** and **HF12**, at the **T1**, **T2C**, and **T2** timepoints. Define these shared taxa as core resistance-associated biomarkers.
- Visualize species-level composition with stacked bar plots and differential species with volcano plots or heatmaps; summarize shared resistance-associated markers using an UpSet plot.
