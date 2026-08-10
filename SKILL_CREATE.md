# Skill migration prompt (for **developers / coding agents**)

You are working in the **openclaw-microbiome** repo. Goal: migrate a user-specified biology CLI / workflow into this plugin as a **Skill**, so an OpenClaw agent can run it one step at a time.

Before editing, skim existing examples: `skills/shotgun-eggnog/`, `skills/shotgun-metaphlan/`, `skills/16s-import/`, plus `workspace/registry/runtimes.yaml` and `examples/microbiome-refs.yaml`.

---

## Workflow (follow in order)

### 1. Clarify the target

Ask the user for:

- Tool name, purpose, typical inputs/outputs
- **GitHub (or other) repository URL** (if they already have a local path, use that — do not re-clone)
- CLI wrapper only vs also a reference script under `scripts/`
- Conda: existing env name, or whether to create / infer install from upstream docs

Do not guess repository URLs.

### 2. Fetch sources (temporary)

- Clone **outside** the skill tree, e.g. `_vendor_src/<tool-name>/` (create if needed)
- Shallow clone is enough: `git clone --depth 1 <url> _vendor_src/<tool-name>`
- Read README / CLI `--help` / entrypoints: executables, subcommands, key flags, reference DBs, recommended conda/pip install
- **Do not** vendor the whole upstream repo into `skills/`; keep only `SKILL.md` and optional slim reference helpers

### 3. Inject into this plugin

Minimal edits:

| Action | Path |
|--------|------|
| Register or extend runtime | `workspace/registry/runtimes.yaml` (`conda_env` + `tools` allowlist) |
| New reference DB ids (if needed) | `examples/microbiome-refs.yaml` (`relative_path` or tree-exception); **never** hardcode host DB paths in the skill |
| New skill | `skills/<name>/SKILL.md` (`<name>` = kebab-case, same as frontmatter `name`) |
| Optional helpers | `skills/<name>/scripts/*` |
| Index (OpenClaw-visible) | `workspace/AGENTS.md` skill map — this is agent bootstrap context. Do **not** treat repo-root `README.md` as OpenClaw prompts. |

User-side DB deploy remains: `~/.openclaw/microbiome-refs.yaml` + `npm run sync-refs`. In the skill body: read `registry/references.yaml`; if missing, ask the user.

### 4. Clean up temporary sources

When migration finishes (or the user aborts):

- **Ask** whether to delete the temporary clone (`_vendor_src/<tool-name>/` or the path you used)
- Delete only after explicit approval; otherwise keep it and report the path
- Do not delete directories the user already owned that you did not clone for this task

---

## SKILL.md rules

Frontmatter:

```yaml
---
name: <name>
description: >
  What it does and when to use it.
runtime: <runtime-id>      # key in runtimes.yaml
conda_env: <conda-env>
tools:
  - <executable>
---
```

Body minimum: `#` title, `## Runtime` table, `## Agent procedure` (stage → optional DB resolve → run → `analysis/<name>/`).

Optional: `## Reference script`, `## Ask the user when unknown` (only provenance-sensitive choices).

Hard rules:

- **One analysis step per skill**; multi-stage OK inside one skill if steps are run separately
- I/O: `stage/` → `analysis/<name>/`
- If `scripts/` exist: cite skill-relative `scripts/foo.py`; **copy/adapt into the job**; examples must not invoke `skills/.../scripts/` in place or use the skill tree as cwd
- Never mention `mgx_create_job` in a skill; never hardcode host DB paths; never instruct fabricating results

Match helper style to `skills/shotgun-eggnog/scripts/annotate_eggnog.py` (parameterized paths + `conda run`).

---

## Report back to the user

- Files added/changed
- Runtime / skill names and how to run (`conda run -n …`)
- If new ref ids: user must edit `microbiome-refs.yaml` and sync
- Temporary clone path and whether it was deleted per their decision
