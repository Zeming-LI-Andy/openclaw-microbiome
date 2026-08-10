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
| `workspaceRoot` | Agent workspace for `.current_job_id` + generated `registry/references.yaml` |
| `refsConfig` | User refs yaml (default `~/.openclaw/microbiome-refs.yaml`) |
| `refsMode` | `auto` / `docker` / `host` for generated `path` values |
| `catalogDir` | Override `catalog/` for tools.yaml |

`enabled` / install control **whether** tools & skills appear.  
`config.*` control **where** jobs, refs sync, and references.yaml go — they do
not replace the `"skills": ["./skills"]` manifest declaration.

## Long-running analysis (`exec`)

Microbiome CLIs often exceed the default **exec process timeout** (~30 min).
Workspace guidance (`workspace/CODING.md`) uses **background `exec`** with
`timeout: 0` and exit wake — not cron poll loops.

Recommended gateway settings in `~/.openclaw/openclaw.json` (reload gateway
after change):

```json5
{
  tools: {
    exec: {
      // default true: wake when a backgrounded exec exits
      notifyOnExit: true,
      // default false: also wake on successful exit with **no** captured stdout
      // (needed if the agent redirects everything to a log file without tee/echo)
      notifyOnExitEmptySuccess: true,
    }
  }
}
```

| Key | Default | Meaning |
|-----|---------|---------|
| `tools.exec.notifyOnExit` | `true` | System event + heartbeat when a backgrounded exec exits |
| `tools.exec.notifyOnExitEmptySuccess` | `false` | Also notify when exit code is 0 and session stdout is empty |

These are **gateway config**, not per-call `exec` parameters. Agent-side still
prefer `… 2>&1 | tee <job>/reproducibility/logs/<step>.log` so progress is on
disk and the session captures output for wake.

See also: [Background exec](https://docs.openclaw.ai/gateway/background-process).

## Session job

```text
mgx_create_job
  → reuse OPENCLAW_SESSION_JOB_ID
  → else reuse workspace/.current_job_id
  → else create jobsRoot/<YYYYMMDD-HHMMSS-hex>/
       stage/  analysis/  reproducibility/
  → write .current_job_id
```

All analysis artifacts for that conversation stay under that job directory.

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
