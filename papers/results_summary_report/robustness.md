# Robustness experiment — protocol (Case 1)

**Manuscript role:** Results robustness; Methods evaluation.  
**Base case:** Case 1, tomato rhizosphere bacterial-wilt (NCBI BioProject PRJNA777724; Yin et al., *Microbiome* 2022).  
**Analysis prompt set:** `papers/case_studies_design/case_study_1/robustness/prompt_{detailed,medium,simple}.md`  
**Staged inputs:** `papers/case_studies_design/case_study_1/robustness/stage/`  
**Not used:** the full-pipeline `papers/case_studies_design/case_study_1/prompt.md` (raw FASTQ → DADA2).

These notes record **how the experiment is run**, not completion rates or biological numbers. Score after the protocol is frozen. Each replicate is a new OpenClaw conversation.

---

## Question

Does MicroBioAgent finish the same Case 1 analysis under variation of **model** and **prompt granularity**, and do the 16S α/β diversity products stay consistent across repeats?

Robustness is **orthogonal** to ablation: the full system (patched OpenClaw, plugin skills, `CODING.md`) stays on. Only the user prompt and the LLM change.

---

## Design

**Matrix:** 3 models × 3 prompt granularities × 3 independent runs = 27 sessions.

| Factor | Levels | What is held fixed |
|--------|--------|--------------------|
| LLM | three models (names recorded per run) | prompt, workspace, skills, patch, data |
| Prompt | detailed / medium / simple | model (when scoring that axis), data, system |
| Repeat | 3 new conversations | same model + same prompt file |

Do not cross this matrix with ablation conditions. Do not continue a previous session. Do not reuse a previous `job_id`.

---

## Task (same scientific goal in every cell)

Rhizosphere **16S** and matched **shotgun** from a tomato wilt experiment: **4 cultivars × 3 timepoints × 3 biological replicates** in the prompt statement. Cultivars: A57 (susceptible control), HG70 (susceptible male parent), HG64 (resistant female parent), HF12 (resistant F1). Shared resistance markers are defined on **HG64** and **HF12** at **T1**, **T2C**, and **T2**.

The three prompts differ **only** in how much method is specified:

| Prompt | What the agent is told |
|--------|------------------------|
| `prompt_detailed.md` | SOP: Shannon; weighted / unweighted UniFrac and Bray–Curtis; weighted-UniFrac PCoA; PERMANOVA + PERMDISP; taxonomy + DA; UpSet of shared HG64∩HF12 markers; the same DA on shotgun species. |
| `prompt_medium.md` | The same analysis **goals** (characterize data; 16S diversity / taxonomy / DA; shotgun taxonomy / DA; shared markers at T1/T2C/T2). Metrics, tests, and figure types are left to the agent. |
| `prompt_simple.md` | Two sentences: analyze the 16S + shotgun wilt experiment and identify microbiome patterns associated with resistance. |

Prompts list **tasks**, not file paths. Data reach the agent by copying `robustness/stage/` into that session’s job `stage/`.

---

## Frozen inputs

Upstream compute that is **not** the robustness question is frozen so repeats measure the agent, not DADA2 or KneadData noise.

**16S** (`stage/16s/`): post-DADA2 ASV table (`.qza` / `.tsv`), representative sequences, rooted tree, DADA2 stats, sample metadata, amplicon sample table. Do not re-import FASTQ, re-run DADA2, or rebuild the tree.

**Shotgun** (`stage/shotgun/`): metadata plus paired FASTQ in `reads/` — KneadData-cleaned libraries randomly subsampled to **20%** of reads (`seqtk`, seed 42; 36 libraries). Do not re-run KneadData.

**Off-limits:** precomputed diversity / PERMANOVA / figures under `PRJNA777724/qiime2_16s_outputs/diversity/` (except the frozen rooted tree), existing MetaPhlAn tables, KneadData directories, raw FASTQ, and project helper scripts. Reuse of those products would make five runs look identical for the wrong reason.

The 16S metadata already carries corrected HG64 T2/T2C labels. 16S also includes T3/T3C; shotgun does not. Prompts keep the original “3 timepoints” wording for the shared-marker task (T1, T2C, T2).

---

## Run procedure

1. Install the **full** MicroBioAgent workspace (`AGENTS.md`, `TOOLS.md`, `CODING.md`, `IDENTITY.md`, `registry/`) and the **patched** OpenClaw gateway. Load plugin skills.
2. Copy `robustness/stage/` into a **new** session job `stage/` (or equivalent bind). Do not point the agent at the original `PRJNA777724/` analysis tree.
3. Paste **one** of the three prompts as the user message. Confirm the plan if the agent asks; then do not coach methods.
4. After the session ends (or is marked blocked), archive `job_id`, model id, prompt file, transcript, and `analysis/`.
5. Repeat until the 3 × 3 × 5 matrix is filled.

Zero intervention except safety / disk failure. A hang or timeout is a failed replicate; record the last finished step.

---

## Scoring

Primary: **task completion** on a rubric aligned to the detailed prompt’s sections (data characterization; 16S α; 16S β; 16S taxonomy/DA; shotgun taxonomy/DA). Each item 0 / 0.5 / 1 by whether the required artifact exists and is usable — not by fluent chat.

Secondary (from the same runs; freeze the 16S table so this is agent-choice variance):

- Shannon vectors: correlation / ICC across the five repeats of a cell.
- Distance matrices: Mantel, separately for each metric the run actually produced.
- Ordinations: Procrustes (do not compare raw PCoA coordinates).
- Discrete decisions: rarefaction depth, metrics chosen, PERMANOVA formula.

Also record protocol adherence (did a detailed-prompt run use Shannon and the three β metrics?) so a complete but method-wrong job is not scored as a scientific success.

*n* = 5 is a repeatability screen. Report rates with intervals; do not treat a 5/5 cell as proof that the model is insensitive.
