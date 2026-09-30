# Case study 1 — targeted patch ablation during a running analysis

## Purpose

This experiment tests the two runtime capabilities reported in Table 5 of the
manuscript:

1. **Plan updated during execution:** while a real QIIME 2 command is still
   running, the agent yields the session, receives a user message, and changes
   its pending analysis plan before the command exits.
2. **Automatic wake after tool exit:** after the agent yields again, command
   completion resumes the same session without another user message.

The experiment uses the Case study 1 tomato-rhizosphere 16S data. It evaluates
session control during a long microbiome command, not reproduction of the
biological conclusions of Case study 1.

## Design

| Factor | Levels |
|---|---|
| Runtime | `patched`, `unpatched` |
| Replicates | 3 independent conversations per runtime |
| Total | 6 sessions |

The two runtime conditions must be identical except for the
`openclaw-exec-session-wake` patch pack:

- **Patched:** the version-pinned OpenClaw runtime with the patch applied.
- **Unpatched:** the same pinned OpenClaw version without the patch.

Use the same model and model settings, workspace prompts, microbiome skills,
registries, staged inputs, initial prompt, intervention prompt, and host
resources in both conditions. In particular, use the same workspace files for
`patched` and `unpatched`; changing the prompts would confound the patch test.
Run every replicate in a new conversation with a new `job_id`.

## Inputs

Use the frozen post-DADA2 Case study 1 inputs under the robustness `stage/16s/`
directory:

- ASV feature table;
- representative sequences;
- rooted tree;
- DADA2 statistics;
- sample metadata.

Copy the frozen input tree into the new job's `stage/` directory. Do not use an
existing taxonomy artifact or another session's analysis outputs.

## Pilot selection of the running task

Before scored runs, pilot the configured QIIME 2 taxonomy classifier on the
same inputs. The selected command must:

- run for long enough that the standardized intervention can be sent while the
  process is still alive;
- enter background execution and return a valid execution session identifier;
- complete successfully and reproducibly on the test host;
- normally leave at least two minutes between intervention delivery and tool
  exit.

The pilot is not scored. If a scored command exits before the intervention is
sent, that run did not test in-run feedback and must be marked invalid and
repeated. Record any excluded run and its reason rather than silently deleting
it.

## Standardized prompts

- Start each session with `initial_prompt.md`.
- Send `intervention_prompt.md` verbatim while the taxonomy-classification
  process is confirmed to be running.
- Do not send a subsequent `continue`, reminder, or recovery message.

## Procedure for each replicate

1. Start a new OpenClaw conversation and create a new microbiome job.
2. Copy the frozen Case study 1 16S inputs into the job's `stage/` directory.
3. Send `initial_prompt.md` and approve the initial plan if normal operation
   requires plan confirmation. This confirmation is not counted as an
   intervention.
4. Allow the agent to start the QIIME 2 taxonomy-classification command. Record
   the execution session identifier, operating-system PID when available, and
   command start time.
5. Confirm from outside the conversational turn that the process is still
   running. Record this observation and its timestamp.
6. Send `intervention_prompt.md` while the process is running. Record the user
   message timestamp.
7. Do not terminate or restart the command. Do not manually poll it through the
   conversation. Do not send another user message.
8. Observe whether the agent processes the intervention before tool exit and
   whether it calls `sessions_yield` again.
9. Record the command exit time and exit status. After tool exit, wait for up
   to five minutes without sending a message and observe whether the completion
   event starts the next agent turn.
10. Archive the transcript, job directory, process and gateway logs, and the
    completed run record.

The operator should alternate patched and unpatched runs where practical so
that host load or time-of-day effects are not aligned with one condition.

## Scoring

### 1. Plan updated during execution

Score a session as successful only when all of the following are supported by
timestamps and the transcript:

- the taxonomy-classification process was running when the intervention was
  submitted;
- the agent processed the intervention before that process exited;
- the revised pending plan removed the pooled resistant-versus-susceptible
  comparison;
- the revised plan added separate T1, T2C, and T2 comparisons;
- the revised plan added a significant-genera heatmap;
- the current taxonomy-classification command was retained rather than
  cancelled or restarted.

An acknowledgement such as “received” is insufficient unless the pending plan
is explicitly revised. If the queued message is handled only after tool exit,
score this endpoint as failure.

### 2. Automatic wake after tool exit

Score a session as successful only when:

- the agent has yielded control after handling the intervention;
- the taxonomy-classification process exits;
- no new user message is sent after the intervention; and
- the tool-exit event starts a new agent turn in the same session within five
  minutes.

Manual `continue` messages, operator polling that causes a new turn, or a wake
from an unrelated scheduled event do not count as success.

Report both endpoints as the number of successful sessions out of three. The
main-text table contains only these two outcomes. Process identifiers,
timestamps, exit status, plan text, wake-event provenance, and subsequent
artifacts belong in the Supplementary audit table.

## Run-record template

Create one copy of the following table for every session:

| Field | Value |
|---|---|
| Condition | patched / unpatched |
| Replicate | 1 / 2 / 3 |
| Model and settings | |
| `job_id` | |
| Conversation/session ID | |
| Exec session ID | |
| Process PID | |
| Tool start time | |
| Intervention time | |
| Tool exit time and status | |
| Plan-update time | |
| `sessions_yield` after update | yes / no |
| Wake time | |
| Wake-event source | |
| Plan updated during execution | pass / fail |
| Automatic wake after tool exit | pass / fail |
| Transcript path | |
| Gateway/process log paths | |
| Notes or exclusion reason | |

## Aggregate result format

| System | Plan updated during execution | Automatic wake after tool exit |
|---|---:|---:|
| Patched | successful sessions / 3 | successful sessions / 3 |
| Unpatched | successful sessions / 3 | successful sessions / 3 |

