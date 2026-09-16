# Case study 1 — ablation workspaces

Operator only. Each subdirectory is the OpenClaw workspace prompt set for one
condition. Merge that directory’s `*.md` into the agent workspace (keep
`registry/` from the plugin workspace). One conversation per replicate; use the
same analysis prompt as the robustness detailed run.

Do not tell the agent which condition it is in.

| Directory | Ablate | Workspace prompts | Runtime |
|-----------|--------|-------------------|--------|
| `full/` | — | Current plugin workspace (control) | Patched OpenClaw + plugin skills |
| `no_patch/` | exec-session-wake pack | Same as `full/` | **Unpatched** OpenClaw; skills on |
| `no_skills/` | Skills | No `plugin-skills/` pointers | Patched OpenClaw; **do not load** plugin skills |
| `no_coding/` | `CODING.md` | No coding guide; no yield / one-step rules | Patched OpenClaw; skills on |

`no_skills` must also disable skill loading (empty plugin `skills`, or equivalent).
Editing AGENTS/TOOLS alone is not enough — OpenClaw still injects skill descriptions.
