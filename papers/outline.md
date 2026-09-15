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
