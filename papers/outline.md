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
4. Asynchronous human guidance: a user can revise pending analysis while a
   real tool remains running, and the same session resumes automatically after
   completion; a targeted patched-versus-unpatched experiment must demonstrate
   this behavior rather than leaving it as an architectural claim.

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

**Problem solved.** Microbiome researchers face a tension between standardized
workflows and study-specific analysis. A fixed whole-analysis pipeline is
reproducible but prespecifies the route; an unconstrained agent is flexible but
must still execute heterogeneous, multi-hour bioinformatics tools reliably.
In practice, the software ecosystem is distributed across command-line tools,
programming languages, runtime environments, file formats and reference
databases. Turning their separate outputs into a coherent biological analysis
therefore demands both computational proficiency and microbiome domain
knowledge, creating a substantial entry barrier.
MicroBioAgent addresses this tension by preserving standardization at the
**step level** while allowing the agent to compose and revise the
**study-level workflow**. It applies this model across the upstream and
downstream stages of 16S, reference-based shotgun and assembly/MAG analysis,
runs sequencing-data computation locally, and remains open to user guidance
during long-running steps.

**Why it matters.** The system is intended to let a researcher move from a
biological question and sequencing data to inspectable taxonomic, functional
and genome-resolved outputs without first engineering a complete pipeline for
that study or manually coordinating every command, environment, database and
file hand-off. It organizes fragmented tool knowledge and intermediate results
into one goal-directed analysis process. Local execution keeps raw reads
within the user's computational environment, while mid-analysis feedback lets
the researcher retain control over decisions that arise after computation has
begun. The practical significance is a lower operational barrier to
microbiome analysis, especially for researchers with biological expertise but
limited programming experience, while preserving inspectable steps and human
scientific judgement.

Use **five connected paragraphs**, without a separate `Related work`
subsection. Aim for roughly 700–900 words in the eventual Introduction. Follow
the same argumentative discipline as MetaClaw's Introduction—domain problem,
existing solutions, precise unresolved problem, needed operating model, and
contributions—while making our unresolved problem and contribution distinct.

| Paragraph | Argument and content | Evidence / citation role | Transition |
|-----------|----------------------|--------------------------|------------|
| **1. Why microbiome analysis is difficult and hard to enter** | Begin with the scientific goal: connecting microbial community structure and functional potential to phenotype or environment. Explain that 16S amplicon, reference-based shotgun and assembly/MAG routes answer different questions and produce different objects—ASVs and diversity, taxa/genes/pathways, or reconstructed genomes and metabolic potential. The corresponding tools are fragmented across command-line interfaces, languages, environments, file formats and databases. Selecting appropriate methods, executing them correctly and consolidating their outputs therefore requires programming ability together with microbiome and statistical knowledge. Studies may need one route or a study-specific combination, further raising the entry barrier. | Cite authoritative best-practice/workflow papers and empirical software papers that explicitly describe command-line learning curves, dependency complexity or fragmented resources. Use tool names only as examples. | The field has mature software for these stages, but accessibility and study-level coordination remain separate concerns. |
| **2. What established tools and workflow systems solve—and their boundary** | QIIME 2, bioBakery and MAG toolkits provide validated domain methods; Snakemake/Nextflow and domain pipelines make predefined workflows reproducible and scalable. Graphical and web platforms improve access for particular analyses. A predefined workflow, however, assumes that a suitable complete route has already been selected and encoded, while graphical platforms generally expose a bounded collection of analyses. When a study crosses analysis families, changes direction after inspecting an intermediate result, or requires optional annotation, researchers still need to connect methods and interpret their outputs. Frame this as the boundary of predefined or bounded interfaces, not a defect in individual tools. | Cite QIIME 2, bioBakery, metaWRAP/Aviary, workflow managers and one suitable accessibility-oriented microbiome platform paper. | LLM agents offer a way to lower the interface barrier while making study-level orchestration adaptive. |
| **3. What bio-agents already solve—and the remaining problem** | AutoBA, Biomni and other bio-agents demonstrate planning, code/tool execution and error recovery. Biomni also evaluates microbiome tasks. MetaClaw, developed independently from this project, is the nearest system: it demonstrates auditable end-to-end metagenomic study reproduction using registered FlowHub workflows upstream and customizable local skills downstream. These works establish that agents can execute bioinformatics; our problem is narrower: no fixed upstream/downstream split or registered whole-analysis flow should determine the study path, and the conversational agent should remain controllable while its local tools run for hours. Do not claim that prior agents cannot plan, cannot run end to end, or cannot receive messages. | Cite primary AutoBA, Biomni, BioAgents and the latest MetaClaw version. Describe MetaClaw's reported architecture and evaluation accurately. | Convert the comparison into the operating model the field needs. |
| **4. The needed operating model and its practical significance** | Use the key sentence: **“What is needed is not another fixed microbiome pipeline, but an accessible and adaptive execution layer that standardizes individual analytical steps while organizing fragmented tools and outputs into a study-level workflow guided by the research goal, available data and verified intermediate results.”** Then add two requirements: sequencing computation and databases can remain local; long-running execution must not close the window for scientific supervision. Explain the concrete benefit: a researcher can express the biological objective instead of first authoring a complete DAG or manually translating between every tool, retain raw data in the local environment, inspect the resulting artifacts, and redirect pending analysis when new observations or priorities arise. This paragraph carries the paper's significance. | Support the entry-barrier premise with literature, then present the operating model as the paper's synthesis. Avoid “first,” “only,” “most comprehensive,” “template-free,” and guaranteed-security language. | Introduce MicroBioAgent as the implementation of this operating model. |
| **5. What we contribute** | Present MicroBioAgent and four linked technical contributions: **(i) analytical breadth**, covering upstream and downstream 16S, reference-based shotgun and de novo/MAG routes plus taxonomic, gene, pathway and metabolism-related annotation; **(ii) adaptive composition**, selecting, connecting, checking and revising step-level skills without a predefined whole-analysis DAG; **(iii) local execution**, resolving user-owned runtimes and references so sequencing-data computation can remain local; and **(iv) asynchronous human guidance**, allowing user feedback while a long step runs and automatically resuming after completion. State their combined user-facing consequence: the agent converts a biological objective into an inspectable end-to-end process and thereby lowers the computational and operational barrier to microbiome analysis. End with the three case studies as demonstrations of the implemented scope; mention interaction traces only if they exist. | Ground contributions in repository components and match case statements to cloud records. Keep implementation details and evaluation metrics out of Introduction. | End with the practical result: broader access to study-specific microbiome analysis without hiding the analytical steps or removing human scientific judgement. |

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
“Lowers the barrier” is supported mechanistically by natural-language goal
specification, agent-generated plans, runtime/reference resolution, command
execution, artifact checks and result organization. Use “substantially” or
“greatly lowers” only if a usability comparison measures time, successful task
completion or required programming interventions against an appropriate
baseline. The system assists with domain decisions and synthesis; it does not
remove the need for biological interpretation and study-design judgement.
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

The Results must establish three layers of evidence in order: what the system
does, whether it works on real microbiome studies, and which design components
make the observed behavior reliable.  Human-in-the-loop is therefore not a
standalone label in the architecture figure: Results Section 3.1 explains the
mechanism, and Results Section 3.4.2 tests the distinctive asynchronous behavior and
the contribution of the exec-session-wake patch.

#### 3.1 MicroBioAgent architecture, analytical scope, and asynchronous guidance

Open with **Figure 1**, the system architecture and analytical landscape.  The
text should explain one complete user-to-result cycle:

1. a biological objective starts a session-bound analysis job;
2. the agent constructs an inspectable plan and selects step-level skills;
3. runtime and reference registries resolve local tools and databases;
4. one step runs at a time and its artifacts are checked before the next step;
5. a long command moves to background execution and the session yields;
6. a user message can revise pending steps without terminating the running
   command; and
7. command completion wakes the same session, which continues under the
   revised plan.

Figure 1 should contain: **(a)** components and data flow; **(b)** the three
analysis families (16S amplicon, reference-based shotgun, and
assembly/genome-resolved shotgun); **(c)** representative shared annotation
and statistical skills; and **(d)** a conceptual timeline showing the two
same-session continuation paths, user feedback and command completion.

This section describes the operating mechanism and implemented scope.  It does
not report HITL success rates or imply that every shipped skill ran in the
cases.  End the section by stating that three public-data case studies test
analytical breadth, while robustness and ablation test reliable operation.  A
forward reference should direct the reader to the targeted HITL ablation in
Results Section 3.4.2.

#### 3.2 Three case studies demonstrate complementary analysis families

Start this section with the evaluation design rather than immediately entering
Case 1.  State that these are **capability-oriented independent reanalyses**, not
exact computational reproductions of the source studies.  Software versions,
reference databases and some statistical procedures differ; evaluation rests
on end-to-end completion, valid artifacts, and recovery of prespecified major
biological signals.

The overview reports 60 tomato 16S libraries and 36 matched shotgun libraries,
128 CRC shotgun libraries, and six enrichment metagenomes: 230 sequencing
library inputs representing 194 distinct biological samples if the 36 tomato
shotgun libraries are confirmed to be a subset of the 60 specimens.  Table 1
maps each case to the capability it tests, its executed stages, primary
artifacts, and main biological concordance criterion.  Detailed datasets,
commands, versions, statistics and session records are reserved under the
stable working identifiers in `papers/supplementary_manifest.md`.

##### 3.2.1 Tomato rhizosphere: amplicon and reference-based taxonomic analysis

**Capability tested.** 16S upstream/downstream analysis, diversity, taxonomy,
differential abundance, and matched MetaPhlAn profiling.

**Result order.** Sample design and completed path; Shannon and weighted
UniFrac results; inoculation-associated community shift and *Ralstonia*
expansion; resistant-versus-susceptible differential abundance; matched
shotgun profiling.  Report the stronger community-level signals before focal
taxa.

Use the two source-study focal species as a prespecified database-sensitivity
analysis.  MetaPhlAn3 recovered *Pseudomonas putida* but did not resolve
*Sphingopyxis unclassified*; MetaPhlAn2 recovered both and found significant
between-phenotype differences.  Show both versions transparently and report
database builds, detection prevalence, effect sizes, tests, P values and
adjusted P values in the Supplementary table.  Call this agent adaptation only
if the archived trace shows that the agent itself diagnosed and changed the
version; otherwise call it an investigator-guided sensitivity analysis.

##### 3.2.2 Colorectal cancer: taxonomic, functional, and predictive analysis

**Capability tested.** Reference-based shotgun profiling with MetaPhlAn3 and
HUMAnN3, beta diversity, species and functional differential analysis, and
gene-family/KO classifier construction.

Report the 128-sample C1 design; beta-diversity tests; recovery in the same
direction of prespecified CRC-associated taxa; gene-family and KO results; and
nested-cross-validation performance.  The classifiers demonstrate an
end-to-end analytical route.  They do not reproduce the source study's
20-gene marker panel or its external validation, and no new diagnostic marker
is claimed.

##### 3.2.3 Enrichment metagenomes: assembly, MAG recovery, and functional annotation

**Capability tested.** Assembly-based/genome-resolved analysis: assembly,
binning/refinement, MAG quality control, dereplication, taxonomy, abundance,
and focal-genome functional annotation.

Report the six metagenomes; 151 HQ/MQ MAGs and 73 representatives after 95% ANI
dereplication; dominant focal taxa; and annotated gene repertoires relevant to
alkane oxidation, oxidized-derivative degradation and beta-oxidation.  Because
the source study and reanalysis use different GTDB releases and annotation
systems, claim recovery of principal taxonomic and functional patterns, not an
identical MAG catalogue.  State that each enrichment is one metagenome and
that predicted CDS counts are neither expression measurements nor direct
evidence of substrate degradation.

#### 3.3 Robustness across models and prompt granularity

Use the frozen Case 1 inputs and the full system in a
3 models × 3 prompt granularities × 3 independent runs design (27 sessions).
The primary result is artifact-level completion of common scientific goals;
method-specific adherence is scored only when the detailed prompt requested
that method.  Secondary results quantify repeat consistency of Shannon values,
distance matrices and ordinations.  Report individual runs and uncertainty;
3/3 is an initial repeatability result, not proof of invariance.

Main text: one compact heatmap or dot plot of completion by model and prompt.
Supplementary: all session-level scores, analysis choices, pairwise
correlations, Mantel tests and Procrustes results.

#### 3.4 Ablation identifies components required for reliable execution

##### 3.4.1 End-to-end component ablation: completion, artifacts, and efficiency

Compare `full`, `no_skills`, `no_coding`, and `no_patch` under one model, the
same detailed Case 1 prompt, the same frozen inputs, and three independent runs
per condition.  No mid-run user feedback is supplied.  The three core outcomes
are completion of nine requested task outputs, adherence to eight specified
methods, and total token use.  Break task completion down by output type so
omissions can be localized.  Raw token use must be interpreted together with
completion because an early stall can consume fewer tokens by doing less work.

The `no_patch` condition here asks whether an otherwise autonomous end-to-end
analysis reliably resumes after a background command.  It is distinct from
the targeted interactive test below.

##### 3.4.2 Targeted patch ablation: feedback during a running analysis

This subsection is the direct Results evidence for the asynchronous HITL
claim.  Use a short, real Case 1 16S task rather than HUMAnN3.  A pilot selects
a QIIME 2 taxonomy-classification input that runs long enough to enter
background execution but normally completes within minutes.  The pilot is not
scored and the task must not be lengthened with an artificial sleep.

The initial pending plan pools resistant and susceptible samples across
timepoints.  After taxonomy classification is confirmed running and the
session yields, send the same instruction in every run: keep the current
classification process, replace the pooled comparison with separate T1, T2C
and T2 comparisons, and add a significant-genera heatmap.  The agent must
incorporate the instruction and yield again while the same command remains
running.  No later `continue` message is allowed.

Compare complete MicroBioAgent (three runs) with an otherwise identical
unpatched runtime (three runs).  A session succeeds only if all of the
following hold:

1. the running taxonomy process is neither terminated nor restarted;
2. the user instruction is incorporated into the pending plan;
3. command completion resumes the session without another user message;
4. T1, T2C and T2 comparison artifacts and the requested heatmap are created;
5. the cancelled pooled comparison is not executed; and
6. no analysis step is duplicated.

The primary endpoint is interactive-continuation success (all criteria met).
Report each criterion separately, plus feedback-to-plan-update and
tool-exit-to-resumption latency.  Token use may be retained in Supplementary
records but is not the primary endpoint.  A representative timestamped trace
and full-versus-unpatched outcome plot should appear in the main ablation
figure; all six transcripts, timestamps and artifact checks belong in
Supplementary tables.

This subsection supports the bounded claim that MicroBioAgent accepts user
feedback while a long-running tool continues, revises pending analysis, and
automatically resumes after tool completion.  It does not claim that HITL in
general is novel: M3A evaluates checkpoint-based HITL by pausing after each
step, whereas this experiment tests asynchronous feedback during a running
tool.

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

The Methods should explain the study design and the reproducible operating
principles at the level needed to assess the claims.  Avoid internal API names,
job-directory layouts, registry field names, and command-by-command pipeline
instructions.

#### 4.1 MicroBioAgent system overview

Describe the system as an agent that maintains study context, produces an
inspectable plan, chooses modular analytical procedures according to the
scientific objective and verified intermediate products, and reports failed or
unavailable steps without inventing results.  This section explains the
system's operating principles; Results Section 3.1 describes the implemented
analysis families shown in Figure 1.

#### 4.2 Skill-guided analysis and configured local execution

Explain how `TOOLS.md` connects tool use, microbiome procedures, configured
software environments, and reference resources.  Emphasize that procedures
encode method-specific requirements without forcing a fixed end-to-end
template.  Raw-read computation can remain in a user-controlled environment;
state separately that optional public annotation services may receive query
information.  Describe output inspection as procedure-specific artifact
checking, not as a universal validation engine.  Summarize analytical breadth
by family rather than listing internal skill identifiers.

#### 4.3 Long-running execution and asynchronous human guidance

Explain the behavior specified by `CODING.md`: one principal operation is
completed and inspected before dependent work; a still-running command
continues after the conversation yields; either a user message or tool-exit
event can reactivate the same session.  A user message may revise pending work
without terminating the running command, and the version-pinned runtime patch
provides reliable automatic wake and continuation after command completion.

#### 4.4 Case study design

Introduce the three datasets as capability-oriented reanalyses rather than
exact computational reproductions.  Define the common evaluation logic:
completion of the requested analysis, usable artifacts, and recovery of
biological signals selected from each source study before inspecting the new
results.  Numerical identity is not required when software, databases, or
statistical procedures differ.

##### 4.4.1 Tomato rhizosphere case

Report the 60 V3–V4 16S samples and 36 matched shotgun libraries, the cultivar
and time-point design, DADA2 and QIIME 2 taxonomy, alpha/beta-diversity methods,
PERMANOVA/PERMDISP, MaAsLin 3 differential analysis, and MetaPhlAn3/2
database-generation sensitivity analysis for the two prespecified taxa.

##### 4.4.2 Colorectal cancer case

Report the C1 cohort (74 CRC and 54 control samples), MetaPhlAn3 and HUMAnN3
profiles, beta-diversity and differential tests, the positive species network,
and gene-family/KO classifiers evaluated by nested cross-validation.  Frame the
classifiers as execution of a complete analytical design within this cohort,
not as external clinical validation.

##### 4.4.3 Genome-resolved enrichment case

Report the six enrichment metagenomes, MAG quality thresholds, 95% ANI
dereplication, GTDB R232 assignment, CoverM abundance estimation, and focal-MAG
eggNOG interpretation.  Treat abundance patterns descriptively because each
inoculum–substrate combination has one metagenome, and describe gene counts as
predicted coding potential.

#### 4.5 Robustness and ablation experiments

##### Robustness across models and prompt granularity

Use the frozen Case 1 inputs in a 3 models × 3 prompt granularities × 3 runs
design (27 sessions).  Score artifact-level completion, method adherence for
detailed prompts, and repeat consistency of Shannon vectors, distance
matrices, and ordinations.

##### End-to-end component ablation

Compare the complete system, no patch, no microbiome skills, and no coding
guidance using one model and three sessions per condition (12 sessions).  Score
nine requested task outputs, adherence to eight specified methods, and total
token use.  Interpret tokens together with completion.

##### Targeted patch ablation during a running analysis

Compare patched and unpatched runtimes in three sessions each using a real
Case 1 QIIME 2 taxonomy command.  During execution, replace the pooled
phenotype comparison with separate T1, T2C, and T2 comparisons and add a
significant-genera heatmap.  The two primary outcomes are whether the pending
plan is updated while the tool runs and whether tool exit automatically wakes
the same session.  Runs in which the command ends before intervention are
excluded and repeated with the reason retained.

#### Data availability and Code availability

Place these after Methods as separate article sections.  Data availability
covers source accessions, sample mapping, deposited derived data, and limits on
redistribution.  Code availability covers the repository, tagged release,
license, environment specifications, analysis scripts, runtime pin, patch, and
immutable archive DOI.

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
| **Fig. 1** | Results 3.1 | Integrated system figure: architecture and data flow; 16S / reference-based / assembly families; representative skills; asynchronous user-message and command-completion timeline |
| **Fig. 2** | Case 1 | Tomato: diversity / taxonomy, MetaPhlAn2/3 sensitivity, and resistance-associated signals |
| **Fig. 3** | Case 2 | CRC: composition, function, differential results, and classifier performance |
| **Fig. 4** | Case 3 | MAG quality/taxonomy, composition, and focal-genome functional annotation |
| **Fig. 5** | Results 3.3 | Robustness: artifact completion across 3 models × 3 prompt granularities, with repeat-consistency summary |
| **Fig. 6** | Results 3.4 | Ablation: end-to-end completion/token efficiency plus targeted patched-versus-unpatched HITL timeline and outcomes |

| ID | Content |
|----|---------|
| **Table 1** | Case-study overview: data, biological samples, sequencing libraries, capability tested, executed stages, and concordance criterion |
| **Table 2** | Related systems comparison in the Introduction |
| **Supplementary** | Skill inventory, detailed case results, all robustness sessions, HITL traces, ablation sessions, token accounting, software and reference versions; working identifiers live in `papers/supplementary_manifest.md` |

Fig. 1 is mandatory.  Keep the representative HITL timeline and its
patched-versus-unpatched outcome in Fig. 6 rather than presenting the
architecture schematic as proof that the behavior works.

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
