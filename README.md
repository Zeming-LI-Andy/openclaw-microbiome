# openclaw-microbiome

OpenClaw plugin for **16S / metagenomics** analysis sessions.

## What it does

- **Plugin tool:** `mgx_create_job` — one OpenClaw conversation ↔ one `job_id`
- **Skills:** `skills/*/SKILL.md` step procedures; optional `scripts/` are
  **reference** helpers (skill-relative paths; copy/adapt into the session job)
- **Registries:**
  - `workspace/registry/runtimes.yaml` — CLIs + `conda_env`
  - `workspace/registry/references.yaml` — **generated** DB paths (`path` only)
- **Execution:** native OpenClaw Bash / Read (not a full MicrobioAgent port)

## What it does not do

- Does not auto-mount Docker volumes into OpenClaw (use `OPENCLAW_EXTRA_MOUNTS`)
- Does not configure agent sandbox binds (out of scope for this plugin)
- Does not ship host-specific DB locations in the repo

## OpenClaw patches (required for background exec wake)

Long steps use background `exec` + `notifyOnExit` wake (see
`workspace/CODING.md`). Carry the pinned upstream fix pack instead of editing
OpenClaw in-place:

- Pack: [`patches/openclaw-exec-session-wake/`](./patches/openclaw-exec-session-wake/)
- Target: see `manifest.json` (**OpenClaw `2026.7.2` @ `35c9c76b8c76…`**)

```bash
./patches/openclaw-exec-session-wake/scripts/apply-openclaw-patches.sh --check
./patches/openclaw-exec-session-wake/scripts/apply-openclaw-patches.sh
# then rebuild OpenClaw and restart the gateway
```

## Install

```bash
cd /path/to/openclaw-microbiome
npm install
npm run plugin:build
openclaw plugins install ./
```

This installs the plugin package (tools + `skills/` via manifest
`"skills": ["./skills"]`). Then enable it and set runtime paths in
`~/.openclaw/openclaw.json` (see **Plugin config** below).

Also merge plugin `workspace/` (AGENTS.md, CODING.md, `registry/`, …) into your
OpenClaw agent workspace — skills load from the plugin; workspace docs/registry
still live in the agent workspace.

## Reference DBs (critical)

Deploy paths live in a **user file**, not in the plugin checkout.

### 1. Create `~/.openclaw/microbiome-refs.yaml`

```bash
mkdir -p ~/.openclaw
cp examples/microbiome-refs.yaml ~/.openclaw/microbiome-refs.yaml
# edit host_path / relative_path to match your machine
```

Schema (preferred: whole-tree root + relative entries). DB metadata comes
**only** from this file — the plugin has no built-in DB catalog:

```yaml
version: 1
refdb_root:
  host_path: /data/refdb
  container_path: /refdb
references:
  silva_ssu_nr99_seqs:
    description: SILVA 138.2 SSURef NR99 full-length reference sequences (.qza)
    kind: file
    relative_path: silva/silva-138.2-ssu-nr99-full-seqs.qza
  # Tree exception:
  # my_custom_db:
  #   description: My custom reference
  #   kind: directory
  #   host_path: /other/custom_db
  #   container_path: /refdb/custom/custom_db
```

### 2. Generate agent-facing `references.yaml`

```bash
npm run build
npm run sync-refs
# or with flags:
# npm run sync-refs -- --refs ~/.openclaw/microbiome-refs.yaml \
#   --workspace /path/to/workspace --mode host
```

Gateway startup also syncs via the plugin `gateway_start` hook when the
microbiome plugin is enabled (`activation.onStartup: true`).

Generated file shape (`workspace/registry/references.yaml`):

```yaml
references:
  silva_ssu_nr99_seqs:
    description: "..."
    kind: file
    path: /refdb/silva/...   # or host absolute path when refsMode=host
```

Agent / skills: use **`references.<id>.path` only**. 

### 3. Docker vs bare-metal

| Mode | `refsMode` | Generated `path` | Mount |
|------|------------|------------------|-------|
| Bare-metal | `host` (or `auto` on host) | `/data/refdb/...` | none — OS paths |
| Docker gateway | `docker` (or `auto` in container) | `/refdb/...` | see below |

**Docker:** mount the host tree into the gateway container with OpenClaw’s
existing env (no OpenClaw core changes):

```bash
export OPENCLAW_EXTRA_MOUNTS=/data/refdb:/refdb:ro
# then run openclaw scripts/docker/setup.sh (writes docker-compose.extra.yml)
```

`npm run sync-refs` prints the recommended `OPENCLAW_EXTRA_MOUNTS` string.

`refsMode` only chooses which path namespace is written into
`references.yaml`; it does not perform the mount.

## Plugin config (`openclaw.json`)

`openclaw plugins install` only **installs** the plugin files. This block in
`~/.openclaw/openclaw.json` **enables** it and passes runtime options into
`plugins.entries.microbiome.config` (validated by `openclaw.plugin.json`
`configSchema`):

```json5
{
  plugins: {
    entries: {
      microbiome: {
        enabled: true,
        config: {
          jobsRoot: "/data/output",
          workspaceRoot: "/path/to/workspace",
          // optional:
          refsConfig: "~/.openclaw/microbiome-refs.yaml",
          refsMode: "auto", // auto | docker | host
        }
      }
    }
  }
}
```

| Key | Meaning |
|-----|---------|
| `enabled` | Load the plugin (tools, skills, `gateway_start`) |
| `jobsRoot` | Analysis jobs root (default `OPENCLAW_JOBS_ROOT` or `./jobs`) |
| `workspaceRoot` | Agent workspace for `.microbiome/session_jobs/` + generated `registry/references.yaml` |
| `refsConfig` | User refs yaml (default `~/.openclaw/microbiome-refs.yaml`) |
| `refsMode` | `auto` / `docker` / `host` for generated `path` values |
| `catalogDir` | Override `catalog/` for tools.yaml |

`enabled` / install control **whether** tools & skills appear.  
`config.*` control **where** jobs, refs sync, and references.yaml go — they do
not replace the `"skills": ["./skills"]` manifest declaration.

## Gateway startup (bare-metal)

`exec` uses the gateway’s `SHELL`; if unset it falls back to `sh` (often
**dash**), where `source` / bashisms fail. Start with bash; keep analysis on
`conda run` (`CODING.md`), not `conda activate`.

```bash
export SHELL=/bin/bash   # avoid dash as exec shell
cd /path/to/openclaw
node openclaw.mjs gateway --port 18789 --verbose
```

Recommended `~/.openclaw/openclaw.json` (restart gateway after edit):

```json5
{
  tools: {
    codeMode: { enabled: false }, // force direct exec/read; avoid Code Mode JS sandbox for CLIs
    deny: ["skill_workshop"],    // block agent skill authoring mid-analysis
    exec: {
      pathPrepend: ["~/miniconda3/bin"], // so `conda` resolves without login profile
      notifyOnExit: true,                // wake agent when background exec finishes
      notifyOnExitEmptySuccess: true,    // also wake if stdout was empty (log-only redirects)
    }
  },
  skills: {
    workshop: {
      autonomous: { mode: "off" }, // default is "auto": self-learning writes workspace/skills/
      approvalPolicy: "pending",   // if workshop is used, require operator apply
    }
  }
}
```

Analysis skills live in **`plugin-skills/`** (`$OPENCLAW_STATE_DIR/plugin-skills`),
not `workspace/skills/`. Keep `workspace/skills/` absent (or empty) so workshop
auto-skills cannot shadow plugin procedures.

Long CLIs: background `exec` + `timeout: 0` + exit wake (`CODING.md`).
See [Exec](https://docs.openclaw.ai/tools/exec) /
[Background](https://docs.openclaw.ai/gateway/background-process).

## Session job

```text
mgx_create_job (per OpenClaw conversation / sessionId)
  → reuse OPENCLAW_SESSION_JOB_ID
  → else reuse .microbiome/session_jobs/<sessionId>
  → else create jobsRoot/<YYYYMMDD-HHMMSS-hex>/
       stage/  analysis/  reproducibility/
  → write .microbiome/session_jobs/<sessionId>
```

Different conversations get different job directories. All analysis artifacts for
a conversation stay under that conversation’s job directory.

## Skills (index)

| Area | Skills |
|------|--------|
| 16S | `16s-import` → `16s-denoise-dada2` → `16s-feature-summarize` → `16s-taxonomy` → `16s-phylogeny` → `16s-diversity` → optional `16s-export` / `16s-picrust2` |
| Shotgun | `shotgun-kneaddata` → `shotgun-metaphlan` → optional `shotgun-humann` / `shotgun-gene-catalog` / `shotgun-eggnog` / `shotgun-vfdb` / `shotgun-rgi` / `shotgun-aviary` |
| Public data | `sra-search`, `ncbi-assembly-proteins` |
| Stats / REST | `stats-*`, `annotation-*` |

## Local check

```bash
npm test
npm run build
npm run sync-refs -- --refs examples/microbiome-refs.yaml --workspace ./workspace --mode docker
npm run dry-run
```
