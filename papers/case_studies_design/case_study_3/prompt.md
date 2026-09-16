Design and execute a complete downstream analysis workflow for colorectal cancer (CRC) versus controls based on metagenomic data.

## Microbial Composition and Diversity

- Characterize microbial community composition and species-level abundance, including:
  - Dominant species
  - Alpha diversity
  - Beta diversity
- Perform PCA/PCoA and clustering based on species abundance to evaluate global microbiome structure differences between CRC and control groups.
- Visualize composition and diversity using stacked bar plots, alpha-diversity boxplots, and PCoA/PCA ordination plots colored by group.

## Differential Species and Clinical Association Analyses

- Compare species-level abundance between CRC and control groups, with multiple-testing correction.
- Assess associations between species abundance and clinical variables, including:
  - CRC status
  - Disease stage
  - Age
  - Sex
  - Other potential confounders
- Develop a CRC classification model based on species abundance, and evaluate it using ROC curves, AUC, sensitivity, and specificity.
- Visualize differential species with volcano plots and heatmaps; show key clinical associations and classifier performance with regression plots and ROC curves.

## Functional Gene, KO, and Marker Panel Analyses

- Perform differential-abundance analysis of CRC-associated functional features using both:
  - HUMAnN gene-family abundance profiles
  - KEGG Orthology (KO) abundance profiles
- Apply multiple-testing correction and rank candidate gene families and KOs by statistical significance and effect size.
- Annotate significant KOs to their corresponding KEGG pathways, modules, and biological functions to identify CRC-associated functional alterations.
- Assess associations of gene-family and KO abundance with clinical variables, including CRC status, disease stage, age, sex, and other potential confounders.
- Evaluate the relationship between CRC-associated microbial species and functional features, including gene families and KOs, to identify potential microbial contributors to altered functions.
- Remove redundant candidate features using correlation-based filtering and perform feature selection (e.g., mRMR) to construct:
  - A gene-family marker panel
  - A KO-based marker panel
  - An integrated functional marker panel combining gene families and KOs
- Perform PCA and clustering based on candidate functional markers, develop a composite CRC functional score/index, and evaluate its diagnostic performance using ROC curves, AUC, sensitivity, and specificity.
- Examine associations between functional markers and CRC stage by comparing early-stage CRC (stages I–II), late-stage CRC (stages III–IV), and controls.
- Visualize differential functional features with volcano plots and heatmaps; summarize species–function associations with correlation heatmaps and marker performance with ROC curves.

## Microbial Co-occurrence Network Analysis

- Perform Spearman correlation analysis of CRC-associated species.
- Construct a species co-occurrence network to identify key microbial taxa with coordinated abundance changes.
- Visualize significant species correlations as a co-occurrence network, highlighting hub taxa and positive/negative associations.
