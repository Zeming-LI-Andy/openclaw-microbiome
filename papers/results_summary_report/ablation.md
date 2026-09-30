# Ablation experiment — protocol (Case 1)

**Manuscript role:** Results ablation; Methods evaluation.  
**Base case:** Case 1, same frozen inputs and **detailed** analysis prompt as the robustness experiment.  
**Workspace overlays:** `papers/case_studies_design/case_study_1/ablation/{full,no_patch,no_skills,no_coding}/`  
**Not varied:** LLM (one primary model), prompt granularity (detailed only), staged data.

These notes record **how the experiment is run**, not which component “wins.” Do not tell the agent which condition it is in. Score after the protocol is frozen. Each replicate is a new OpenClaw conversation.

---

## Question

With the LLM and the user prompt held fixed, which **system components** are required for MicroBioAgent to finish Case 1: plugin-shipped skills, the coding / long-exec protocol (`CODING.md`), and the OpenClaw exec-session-wake patch?

Ablation is **orthogonal** to robustness. It is leave-one-out against a full-system control, not a factorial of models × prompts × components.

---

## Design

**Matrix:** 1 model × 4 workspace/runtime conditions × 3 independent runs.

| Condition | What is removed | What stays |
|-----------|-----------------|------------|
| `full/` | nothing (control) | Patched OpenClaw, plugin skills, `AGENTS.md` / `TOOLS.md` / `CODING.md` / `IDENTITY.md`, registries |
| `no_patch/` | exec-session-wake patch pack | **Same prompts as `full/`**; skills on |
| `no_skills/` | plugin-shipped skills and all pointers to them | Patched OpenClaw, `CODING.md`, job tool, registries |
| `no_coding/` | `CODING.md` and duplicated execution rules in `AGENTS.md` / `TOOLS.md` | Patched OpenClaw, skills, job tool, registries |

`no_patch` is **not** a second rewrite of the workspace markdown. The patch lives in OpenClaw (`patches/openclaw-exec-session-wake/`). Using a different workspace here would confound the test.

---

## Task and data

Same as robustness, detailed cell only:

- User message: `papers/case_studies_design/case_study_1/robustness/prompt_detailed.md`
- Inputs: copy `papers/case_studies_design/case_study_1/robustness/stage/` into the session job `stage/`
- 16S starts from the frozen ASV table, sequences, rooted tree, and metadata
- Shotgun starts from 20%-subsampled KneadData paired FASTQ (36 libraries)

Do not use the original full-pipeline Case 1 prompt (raw FASTQ / DADA2).

---

## What each overlay actually changes

Agent-facing files are written as if the missing piece **never existed**. They do not say “ablation” or “you have no skills.”

**`full/` and `no_patch/`**  
Copies of the production workspace: session ↔ `mgx_create_job`, read `TOOLS.md` and `CODING.md`, discover steps under `plugin-skills/`, `exec` with `yieldMs: 30000` and `timeout: 0`, then `sessions_yield` when the process is still running.

**`no_skills/`**  
`AGENTS.md` / `TOOLS.md` / `IDENTITY.md` no longer mention `plugin-skills/`, skill tables, or “skill-driven” work. `CODING.md` remains (step-at-a-time, `conda run`, long-exec yield) with “skill” wording replaced by “step.”  
**Also disable skill loading in OpenClaw** (empty plugin `skills` or equivalent). Editing markdown alone is not an ablation: the runtime still injects skill descriptions.

**`no_coding/`**  
No `CODING.md`. `AGENTS.md` / `TOOLS.md` keep the job contract (`mgx_create_job`, I/O under the job, `exec` not `terminal`, registries, skills) and a short ban on inventing results. They do **not** keep one-step-at-a-time, `conda run` recipes, `yieldMs` / `sessions_yield`, nohup bans, or the absolute-path rule.  
If only `CODING.md` were deleted, Hard rules in `AGENTS.md` and the shell section in `TOOLS.md` would still teach the long-exec protocol, and the ablation would be weak.

Registries (`runtimes.yaml`, `references.yaml`) are **not** ablated. Keep the plugin workspace registry in every condition so database paths do not drift.

---

## Run procedure

1. Merge that condition’s `*.md` into the OpenClaw agent workspace. Keep `registry/` from the plugin workspace.
2. Gateway: patched image for `full`, `no_skills`, `no_coding`; **unpatched** pin-version OpenClaw for `no_patch` only.
3. `no_skills` only: plugin skills not loaded.
4. New conversation. Copy `robustness/stage/` into the job `stage/`. Paste the **detailed** robustness prompt.
5. Confirm the plan if asked; do not hint at yield, conda env names, or which skill to open. Do not manually resume a hung `no_patch` run — that erases the patch effect.
6. Archive condition, `job_id`, transcript, and `analysis/`. Repeat three times per condition.

---

## Scoring

Score three core outcomes: **task completion**, **method adherence**, and
**total token use**.

Task completion contains nine binary items. A task passes only when its
required output exists and is usable:

1. 16S alpha-diversity results;
2. 16S beta-diversity results;
3. 16S taxonomic table;
4. 16S differential-abundance results;
5. MetaPhlAn table;
6. shotgun differential-abundance results;
7. figures;
8. analysis scripts;
9. analysis report.

For every condition, report both the number of sessions completing each item
(`n/3`) and the mean percentage of the nine items completed across sessions.
This task-level breakdown shows which work is omitted rather than collapsing
all failures into one end-to-end result.

Method adherence is scored against eight methods explicitly requested in the
detailed prompt: sequencing-depth normalization, Shannon diversity, weighted
UniFrac, unweighted UniFrac, Bray--Curtis, weighted-UniFrac PCoA, PERMANOVA,
and PERMDISP. Report the mean percentage used as requested across the three
sessions in each condition.

The condition-specific process checks below are diagnostic evidence and belong
in the Supplementary Information rather than the three-column core outcome
summary.

| Condition | Extra process checks |
|-----------|----------------------|
| `full/` | Baseline: job created, skills read, long CLIs yielded and resumed, outputs under `analysis/<step>/` |
| `no_patch/` | After a long `exec`, does the session **wake and continue** without an operator poke? Wall time to stall. |
| `no_skills/` | Correct conda env and CLI family without `SKILL.md`; invented pipelines; skipped phylogeny / MetaPhlAn |
| `no_coding/` | Mega-scripts vs one step; relative paths / writes outside the job; foreground timeout vs yield; `conda activate` vs `conda run` |

Human interventions are counted. Manual “please continue” on `no_patch` is a failure of that condition, not a completed task.

### Token use and efficiency

Record token use for every session from the same OpenClaw/API accounting
source.  Keep the following fields separate when the provider exposes them:

- uncached input tokens;
- cached input tokens;
- output tokens;
- reasoning tokens;
- total model calls.

Report raw total tokens together with task completion.  A stalled or prematurely
terminated condition can consume fewer tokens only because it completed less
work, so raw token use must not be interpreted as efficiency on its own.  Also
report:

1. tokens per completed task item;
2. tokens for successful sessions only, when a condition has successful runs;
3. tokens consumed before stall or terminal failure;
4. model calls and tool calls per completed task item.

Use one model and the same model configuration across all ablation conditions;
do not convert tokens to monetary cost unless the applicable price and cache
treatment are fixed and reported.  Token use is a primary efficiency outcome
for this end-to-end component ablation.  It is not the primary outcome of the
separate targeted in-flight-feedback experiment, whose endpoints are process
preservation, feedback incorporation, automatic resumption, and revised-plan
fidelity.

Expected failure modes (hypotheses to test, not results): `no_patch` dies on long MetaPhlAn / diversity jobs; `no_skills` uses the wrong tool or env; `no_coding` ignores job layout or blocks on exec timeout. Report all three runs for every condition and retain the full-system control on the same model and prompt.
