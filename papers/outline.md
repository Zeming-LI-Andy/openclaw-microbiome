# Manuscript framework

Living design note for `papers/main.tex`. Biological numbers, figure panels,
and citations stay empty until case-study artifacts are available. Do not treat
this file as the camera-ready paper.

**Working title.** MicroBioAgent: end-to-end 16S and metagenomic analysis
across amplicon, reference-based, and assembly-based workflows.

**Thesis.** The contribution is *MicroBioAgent*, a single conversational
agent that can plan and execute the analysis landscape that today is split
across QIIME 2, bioBakery, and MAG/assembly toolkits — not a new aligner,
assembler, or statistical test. OpenClaw is the runtime platform; name the
system MicroBioAgent in the title, abstract, and results.

**What the paper must prove**

1. Coverage: one system spans 16S, reference-based shotgun, and assembly-based
   shotgun (including MAG recovery and metabolic reconstruction).
2. End-to-end: the agent goes from staged reads/metadata to composition,
   function, and (where relevant) prediction or MAG-level metabolism — not a
   single wrapped CLI.
3. Reliability: robustness and ablation show that skills, session jobs, and
   long-running exec are what make that coverage usable.

Case studies are *demonstrations of coverage*, not three independent biology
papers. Biological findings can be reported, but they are secondary to the
systems claim.

---

## 1. Why this structure

Reviewers will ask: “Is this just ChatGPT calling QIIME?” The paper answers
that in this order:

| Section | Job |
|---------|-----|
| 1. Introduction | Microbiome task heterogeneity → established tools and bio-agents → three integrated contributions → supporting evidence. |
| 2. Results | Landscape, three cases, robustness, ablation. |
| 3. Discussion | Limits, then a short conclusion. |
| 4. Methods | System, evaluation protocols, availability. |

Do **not** lead with tomato / CRC / MAG biology. Lead with the analysis
landscape, then use the cases as existence proofs.

---

## 2. Suggested title and abstract

### Title options

1. **(preferred)** MicroBioAgent: end-to-end 16S and metagenomic analysis across amplicon, reference-based, and assembly-based workflows
2. MicroBioAgent: a conversational agent for full-pipeline 16S, taxonomic, functional, and MAG-based metagenomics
3. MicroBioAgent: skill-oriented automation of 16S and shotgun metagenomic analysis

Lead with the software name. Do not title the paper OpenClaw-Microbiome.

### Abstract skeleton (≈200 words, four beats)

1. **Gap.** 16S, reference-based shotgun, and assembly-based MAG analysis are
   mature but live in different expert toolchains. Workflow managers require a
   predefined DAG; chat agents rarely finish multi-hour, multi-tool jobs.
2. **System.** We present MicroBioAgent, which binds one conversation to
   one analysis job and executes step-level *skills* (QIIME 2, KneadData /
   MetaPhlAn / HUMAnN, Aviary MAG recovery, annotation and metabolism) on host
   conda runtimes, with registries for reference databases and background exec
   for long CLIs. Implementation is an OpenClaw plugin (Methods only).
3. **Results.** Three case studies span the landscape: (i) tomato rhizosphere
   16S + MetaPhlAn in a bacterial-wilt resistance / heritability setting;
   (ii) colorectal-cancer case–control MetaPhlAn + HUMAnN + a supervised
   classifier; (iii) MAG recovery with community composition and metabolic
   potential. Robustness and ablation quantify sensitivity to prompts, models,
   and core system components.
4. **Implication.** Full-pipeline microbiome analysis across amplicon and
   shotgun (reference-based and de novo) can be driven conversationally without
   collapsing those families into a single rigid workflow.

---

## 3. Section plan (maps to `main.tex`)

Top-level order is Nature-style: Introduction → Results → Discussion →
Methods. Implementation detail does not appear before the cases.

### 3.1 Introduction (includes related work)

**Central claim.** We present MicroBioAgent as a microbiome analysis agent
with four integrated capabilities: broad end-to-end analysis across 16S,
reference-based shotgun and assembly/MAG routes with downstream annotation;
goal- and evidence-guided composition of step-level skills rather than a
predefined whole-analysis DAG; local execution of upstream and downstream
computational steps; and an asynchronous workflow that allows user feedback
while a long-running step continues. These are the work's contributions. Case
studies and interaction traces provide evidence for their realized scope.

Use **five connected paragraphs**, without a separate `Related work`
subsection. Aim for roughly 650–850 words in the eventual Introduction;
give the biological and computational motivation more space than software
implementation details.

| Paragraph | Argument and content | Evidence / citation role | Transition |
|-----------|----------------------|--------------------------|------------|
| **1. Biological question and heterogeneous data** | Microbiome research links community composition, genes, pathways and genome-resolved metabolic potential to phenotype or environment. Assay and question determine different paths: 16S amplicon, reference-based shotgun, and assembly-based shotgun/MAG. These are complementary, not interchangeable. Mention representative outputs (ASVs and diversity; species, genes and pathways; MAGs and metabolic annotation), not a long tool list. | Cite authoritative amplicon, read-based and MAG workflow papers (QIIME 2, bioBakery, metaWRAP/Aviary, as appropriate). | One scientific question can require decisions and artifact handoffs across these paths. |
| **2. Computational landscape, stated neutrally** | Explain that amplicon, read-based shotgun and assembly/MAG analyses have mature, specialized tools, and that workflow managers can execute specified pipelines reproducibly. This paragraph establishes what the field can already do and why the three routes have distinct inputs, references and outputs. Do **not** present routine path selection, configuration, intermediate-product checks or failure recovery as an established shortcoming of prior *agents*: several already automate those decisions. | Cite QIIME 2, bioBakery, MAG workflow(s), Snakemake/Nextflow concisely. | Once the established tool landscape is clear, turn to agent systems that coordinate it. |
| **3. Bio-agent progress and nearest neighbour** | AutoBA and Biomni already plan and execute biological analyses; Biomni includes microbiome tasks on existing tables. BioAgents and newer benchmarks show an expanding field. Discuss independently developed MetaClaw as the closest microbiome neighbour: it also uses an agent/skill/job approach and reports amplicon and shotgun capabilities, with a different execution split between FlowHub and local components. State what each work *demonstrates*, not what it supposedly cannot do. | Primary AutoBA, Biomni, BioAgents and MetaClaw references; use the version of the MetaClaw preprint checked at submission. One compact paragraph, no catalogue of product features. | These systems establish the field; now state the distinct contribution of this work. |
| **4. MicroBioAgent: four integrated contributions** | State affirmatively that MicroBioAgent **(i)** supports end-to-end 16S, reference-based shotgun and de novo/MAG analysis plus downstream taxonomic, gene, pathway and metabolism-related annotation; **(ii)** constructs a study-specific analysis plan by selecting and connecting step-level skills, verifies each step's products, and can revise remaining steps instead of submitting every study to a fixed end-to-end workflow or predefined DAG; **(iii)** executes sequencing-data computation locally with user-configured reference resources, allowing raw reads to remain on a user-controlled machine; and **(iv)** supports mid-analysis user feedback through background execution, turn yielding, plan revision and automatic completion wake. Give one concrete feedback example: while step A runs, the user changes a pending step B; the agent updates the plan and uses the new instruction after A finishes. Explain that this is a combined system contribution, without claiming each individual capability is unprecedented. | Ground all four in this repository's skill granularity, runtime configuration, workspace instructions and patch pack. The clear architectural contrast with MetaClaw is agent-directed local execution of individual upstream steps rather than submission to registered FlowHub workflows; do not assert that MetaClaw cannot receive messages. | The contribution motivates the paper's demonstrations. |
| **5. Evidence and scope** | State that three case studies demonstrate the three analysis routes and identify the outputs and study-specific skill sequences actually produced. If intervention traces are available, state that they demonstrate user feedback during a long-running step and the subsequent plan change. Close by returning to the four contributions, without presenting them as hypotheses awaiting confirmation. Keep protocol and metrics for Results/Methods. | Match each empirical statement to cloud job records; distinguish implemented annotation skills from those exercised in the cases. | End Introduction; no detailed Methods or case-study biology. |

**Claim boundaries for drafting.** `skills/` contains 16S, shotgun profiling,
assembly/MAG, gene/pathway, primary-metabolism-related and secondary-metabolism
annotation skills. The Introduction may describe this *implemented scope*;
Results must separately say which skills actually ran in the cloud cases.
“Not dependent on a fixed workflow/template” means that MicroBioAgent does not
require one predefined **whole-analysis** pipeline, DAG or study template. It
does use standardized step-level skills and, for some steps, reference scripts;
these provide tool contracts and execution guidance while the agent chooses,
connects and revises the study-specific sequence. Do not call the system
“template-free.”
`gapseq`, KEGG/MetaCyc and BGC tools support metabolism-related inference and
annotation, not direct measurement of metabolite concentrations. Local tool
execution supports keeping reads local, but remote model providers and API
annotation skills mean “fully offline” or “guaranteed data security” would
require a separately verified deployment. The runtime patch supports a
mid-analysis feedback **design**; actual feedback uptake and race handling
require session-level evidence.

**Fixed contribution wording (use this, not a generic
"prior agents cannot orchestrate analyses" gap):**

> Existing biological agents demonstrate planning and execution, while
> MetaClaw demonstrates auditable metagenomic workflows with cloud-based
> upstream processing. We present MicroBioAgent, which composes step-level
> skills into study-specific analyses rather than relying on a predefined
> whole-analysis workflow, executes both upstream and downstream steps locally
> across amplicon, reference-based shotgun and genome-resolved routes, and
> accepts user feedback while long-running steps continue in the background.

This sentence states what **this work contributes**. It does not assert that no
other system implements any individual capability. The concrete distinctions
from MetaClaw are the agent-directed composition and local execution of
individual upstream steps rather than submission to registered FlowHub
workflows. Whether the feedback loop also differentiates them must be shown
through implementation and interaction traces, not inferred from omission in
a paper.

### 3.2 Results

#### 3.2.1 The analysis landscape (lead result)

Open with **Figure 1**: MicroBioAgent, three families, three cases pinned on
the map. This is the figure a reader should remember.

Text: we do not claim a new 16S algorithm. We claim that MicroBioAgent
can traverse each family end-to-end. Then point to Cases 1–3
as the empirical span.

#### 3.2.2 Case 1 — Tomato rhizosphere and bacterial-wilt resistance

**Role in the paper.** 16S full pipeline *plus* shotgun taxonomic
profiling (MetaPhlAn). Bridges amplicon and reference-based shotgun on a
plant-microbiome genetics question (heritability of resistance via the
rhizosphere community).

**Expected story (fill from the server).**

1. 16S: import → DADA2 → taxonomy (SILVA) → phylogeny → α/β diversity
2. Shotgun: KneadData (if used) → MetaPhlAn
3. Statistics: community ~ host genotype / resistance phenotype;
   heritability or genotype–microbiome association as designed in the study
4. Optional: concordance between 16S taxa and MetaPhlAn species

**What *not* to do.** Do not turn this section into a standalone plant
pathology paper. One results page + one multi-panel figure is enough.

#### 3.2.3 Case 2 — CRC case–control (composition, function, classifier)

**Role in the paper.** Deep *reference-based* shotgun: taxonomy +
community function + a study-specific classifier. This is the bioBakery
family, fully agent-driven.

**Expected story.**

1. MetaPhlAn: case vs control composition, diversity
2. HUMAnN: pathways / gene families, differential abundance or enrichment
3. Classifier: predict case/control from species and/or pathway features;
   cross-validation, baseline (majority / simple richness), feature
   importance
4. Sanity: no leakage; report what the agent actually trained on

**What *not* to do.** Do not claim a new CRC biomarker. Claim that the
agent can *produce* a complete case–control functional + ML analysis.

#### 3.2.4 Case 3 — MAG recovery, composition, metabolic potential

**Role in the paper.** *Assembly-based / de novo* arm: Aviary (assemble,
recover, annotate, cluster) plus composition and metabolism (EggNOG /
Bakta / gapseq / gutSMASH as actually run).

**Expected story.**

1. Assembly and MAG recovery, quality (CheckM2) and taxonomy (GTDB)
2. Community composition from MAG abundances (and/or complementary
   profilers if used)
3. Metabolic potential: pathway completeness, models, or BGC/gut gene
   clusters — whatever the job actually produced
4. Tie-back: this family is unreachable if the agent cannot survive
   multi-hour assemble/recover

#### 3.2.5 Robustness

Report as a compact table or small figure: completion under paraphrase /
repeat / resume. Emphasize *artifact checks*, not fluent chat.

#### 3.2.6 Ablation

One figure or table: each removed component vs completion and intervention
count. The sentence we want: skills + job isolation + exec wake are
necessary for full-pipeline coverage; the LLM alone is not.

### 3.3 Discussion (includes conclusion)

- What “full pipeline” does and does not mean (not every optional skill
  in every study; the agent *selects* a path).
- Human confirmation of the plan is a feature, not a failure of autonomy.
- Compute and reference-DB burden (tens of GB conda + large ref trees).
- Hallucinated paths / invented results are prevented by skill rules and
  “skip, don’t invent” — discuss residual risk.
- Comparison to writing a Nextflow workflow: agents win on *heterogeneous,
  study-specific* paths; workflow managers still win on identical batch
  replay.
- Future: more classifiers as skills, long-read, multi-omics, tighter
  provenance.

**Conclusion (last subsection).** MicroBioAgent can span 16S, reference-based
shotgun, and assembly-based MAG recovery. Cases are the span; robustness
and ablation are what would show the span is the system.

### 3.4 Methods

This is the technical core. Write it from the repo; it does not wait on
cloud results. First sentence: MicroBioAgent is implemented as an OpenClaw
plugin. Do not lead the paper with OpenClaw.

**Design principles**

- Skills, not a hidden mega-pipeline: each `SKILL.md` is one analysis step.
- One OpenClaw conversation ↔ one `job_id` (`mgx_create_job`).
- Agent plans first, then executes; failed steps are skipped with dependents,
  not silently invented.
- Long CLIs: timed-yield `exec` + `notifyOnExit` (requires the pinned
  OpenClaw exec-wake patch).
- Host-owned runtimes and reference DBs (`runtimes.yaml`,
  `microbiome-refs.yaml` → generated `references.yaml`).

**Session job**

```
<job_id>/
  stage/                 # reads, manifests, metadata
  analysis/<step>/       # one skill’s outputs
  reproducibility/logs/
  job.json
```

**Skill map (the “full pipeline” table)**

Group skills the way the paper claims coverage — not as a flat dump.

| Family | Stage | Skills |
|--------|-------|--------|
| 16S | Import → ASV → QC → taxonomy → tree → diversity → export / function | `16s-import`, `16s-denoise-dada2`, `16s-feature-summarize`, `16s-taxonomy`, `16s-phylogeny`, `16s-diversity`, `16s-export`, `16s-picrust2` |
| Shotgun, reference-based | QC → taxonomy → pathways / gene families → gene catalog → annotation | `shotgun-kneaddata`, `shotgun-metaphlan`, `shotgun-humann`, `shotgun-gene-catalog`, `shotgun-eggnog`, `shotgun-vfdb`, `shotgun-rgi` |
| Shotgun, assembly-based | Assemble / recover / annotate / cluster MAGs; genome and metabolism | `shotgun-aviary`, `shotgun-bakta`, `shotgun-gapseq`, `shotgun-gutsmash`, `shotgun-antismash` |
| Shared | Public data, statistics, REST annotation | `sra-search`, `ncbi-assembly-proteins`, `stats-*`, `annotation-*` |

Supervised classification (Case 2) is *not* a dedicated skill. It is an
agent-composed step on MetaPhlAn / HUMAnN tables in the `mgx-base` runtime.
Say this explicitly: the system covers profiling and then allows
study-specific modeling without pretending a generic “classifier skill”
exists.

**Execution model**

- `conda run -n <env>` from the runtime registry
- Absolute paths only; I/O confined to the session job
- Heartbeat / model timeouts sized for multi-hour denoise, HUMAnN, Aviary
- Docker image `openclaw-mgx` = patched OpenClaw + conda stack (methods
  detail; not the intro hook)

**Evaluation design.** Each case is a naturalistic analysis request.
Report: dataset, modalities used, skill sequence, human confirmations /
interventions, wall time, and scientific outputs.

**Robustness (to be specified with the server logs).** Same analysis goal
under controlled perturbations, for example:

- Prompt paraphrase (same intent, different wording)
- Model swap (if more than one LLM was used)
- Repeated trials (completion, not just a single success)
- Interrupted / resumed session (exec wake)
- Missing or wrong reference-DB path (does the agent stop and ask?)

**Ablation (system components, not biology).** Typical knobs that match
this codebase:

| Ablation | What is removed | Expected failure mode |
|----------|-----------------|------------------------|
| No skills | Agent has only raw `exec` / docs | Incomplete or unsafe commands |
| No plan-then-execute | Jump to compute | Missed QC, wrong order, no user gate |
| No session job | Outputs not bound to `job_id` | Scattered files, no reuse after rewind |
| No exec wake | Foreground timeout or no notify | HUMAnN / Aviary / DADA2 never finish in-session |
| No registries | Invented conda / DB paths | Silent wrong DB or crash |

Metrics (fill with real numbers later): task completion rate, fraction of
steps that match the canonical skill order, number of human interventions,
whether key artifacts exist and pass sanity checks (not “the p-value looks
nice”).

**Availability (last Methods subsection).** Plugin repository, skill
versions, OpenClaw pin + patch pack, conda recipes, case-study jobs /
prompts (as much as ethics and data licenses allow).

---

## 4. How the three cases carry the thesis

```
                 Case 1              Case 2              Case 3
              tomato 16S+MP       CRC MP+Humann+ML      MAG + metabolism
                    │                   │                    │
                    ▼                   ▼                    ▼
              16S family          Ref-based shotgun    Assembly / de novo
              + taxonomy bridge   + function + ML      + MAG metabolism
                    │                   │                    │
                    └─────────────┬─────┴────────────────────┘
                                  ▼
                     MicroBioAgent / one job model
                     (skills + registries + exec wake)
```

| Case | Primary family | Extra claim | Do not overclaim |
|------|----------------|-------------|------------------|
| 1 Tomato wilt / heritability | 16S end-to-end | Same study also runs MetaPhlAn | New plant-breeding genetics |
| 2 CRC case–control | Ref-based shotgun | Function (HUMAnN) + classifier | New CRC diagnostic |
| 3 MAG | Assembly-based | Composition + metabolic potential | New MAG algorithm |

Together they are the minimum set that justifies “16S + 有参 + 无参/组装
全流程”. Robustness / ablation then justify “this *system* can do it”,
not “we once got lucky”.

---

## 5. Figures and tables

Keep figures in `papers/figures/`. Case panels stay empty until rsync.

| ID | Placement | Content |
|----|-----------|---------|
| **Fig. 1** | Opening Results | Landscape: 16S / ref-based / assembly; skills on the backbone; Cases 1–3 as pins |
| **Fig. 2** | Methods | Architecture: conversation → `mgx_create_job` → skills / conda / refs → `analysis/<step>/`; exec wake |
| **Fig. 3** | Case 1 | Tomato: diversity / taxonomy + MetaPhlAn + genotype or resistance association |
| **Fig. 4** | Case 2 | CRC: composition, pathways, classifier performance |
| **Fig. 5** | Case 3 | MAG quality/taxonomy, composition, metabolic overview |
| **Fig. 6** | Robustness + ablation | Completion / interventions under perturbations and ablations |

| ID | Content |
|----|---------|
| **Table 1** | Skill catalog by family (the coverage table above) |
| **Table 2** | Related systems vs this work (16S / ref / MAG / agent / long-run) |
| **Table 3** | Case-study card: data, *n*, modalities, skills used, wall time, artifacts |
| **Table 4** | Robustness |
| **Table 5** | Ablation |

Fig. 1 is mandatory. If the journal is tight on figures, merge Fig. 6 into
Tables 4–5 and merge Fig. 2 into Fig. 1.

---

## 6. What to write now vs later

| Can draft from this repo now | Needs cloud case artifacts |
|------------------------------|----------------------------|
| Introduction (argument only) | Case sample sizes, phenotypes, accession IDs |
| Related work (after real `.bib` entries) | Actual skill sequences and skipped steps |
| Entire Methods / system section | Figures 3–5 |
| Table 1 (skills) | Table 3 numbers, wall times |
| Fig. 1–2 (schematics) | Robustness / ablation metrics |
| Availability (repo layout, pin) | Prompt logs, intervention counts |

**Writing order**

1. Methods (system) + Table 1 + Fig. 1–2 schematics
2. Introduction (including related-work citations)
3. Results case placeholders, then panels when jobs are synced
4. Discussion + conclusion last

---

## 7. Open decisions (do not block the skeleton)

1. **Venue.** Full methods paper (e.g. *Bioinformatics*, *NAR*,
   *GigaScience*, *mSystems*), not an Application Note — three cases plus
   ablation need the space.
2. **How much biology.** Recommend: one tight paragraph of interpretation
   per case; no extra “discovery” subsection.
3. **Classifier details (Case 2).** Algorithm, features, CV scheme — take
   from the job, do not redesign for the paper.
4. **Case 3 metabolism tool.** gapseq vs EggNOG vs gutSMASH vs antiSMASH:
   report what was run, do not imply all four.
5. **Robustness protocol.** Freeze the perturbation list *before* looking
   at outcomes.
6. **Name in the title.** Use **MicroBioAgent**. OpenClaw is the platform,
   mentioned in Methods, not the product name.

---

## 8. Files in `papers/`

| Path | Role |
|------|------|
| `outline.md` | This framework |
| `main.tex` | Manuscript (English; Intro → Results → Discussion → Methods) |
| `refs.bib` | Real citations only |
| `figures/` | Paper figures (schematics + case panels) |
| `cases.md` | Per-case metadata to fill from the server |
| `build/` | latexmk output (not for git) |
