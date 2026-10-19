# Case study 1 — ablation workspaces

Operator only. Each subdirectory is the OpenClaw workspace prompt set for one
condition. Merge that directory’s `*.md` into the agent workspace (keep
`registry/` from the plugin workspace). One conversation per replicate; use the
same analysis prompt as the robustness detailed run.

Do not tell the agent which condition it is in.

| Directory | Ablate | Workspace prompts | Runtime |
|-----------|--------|-------------------|--------|
| `full/` | — | Current plugin workspace (control) | Patched OpenClaw + plugin skills |
| `no_patch/` | exec-session-wake pack + long-run yield rules | Same as `full/`, with `yieldMs` / `sessions_yield` / anti-polling rules removed from `AGENTS.md`, `TOOLS.md`, and `CODING.md` | **Unpatched** OpenClaw; skills on |
