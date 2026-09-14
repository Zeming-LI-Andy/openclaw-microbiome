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

Do **not** use `ghcr.io/openclaw/openclaw` as the runtime image: those builds
do not include this pack. Check a local checkout first:

```bash
./scripts/check-openclaw-pin.sh --root /path/to/openclaw
```

In-place apply (only when HEAD **is** the pin):

```bash
./patches/openclaw-exec-session-wake/scripts/apply-openclaw-patches.sh --check
./patches/openclaw-exec-session-wake/scripts/apply-openclaw-patches.sh
# then rebuild OpenClaw and restart the gateway
```

If `../openclaw` is newer than the pin, leave it alone and use
`scripts/build-openclaw-mgx-image.sh` (worktree at the pin).

## Conda runtimes (host)

Recipes live in [`environments/`](./environments/) (one file per
`runtimes.yaml` `conda_env`). `stats` and `host` share **`mgx-base`**.

```bash
# Miniforge/Miniconda already on PATH, or: --prefix /opt/conda
./scripts/bootstrap-runtimes.sh --all
./scripts/verify-runtimes.sh
```

Subset: `./scripts/bootstrap-runtimes.sh --only mgx-base,qiime2-amplicon-2024.10`.

Reference DBs are **not downloaded** during bootstrap. In Docker, bootstrap
wires env defaults to `/refdb` (see `--refdb`). Still map the tree in
`microbiome-refs.yaml`.

## Docker image (patched OpenClaw + conda)

```bash
./scripts/build-openclaw-mgx-image.sh
# 1) openclaw:patched  — OpenClaw Dockerfile @ pin + patch pack
# 2) openclaw-mgx:local — Miniforge + all environments/*.yml
```

Then point OpenClaw compose at that image (do not pull GHCR):

```bash
export OPENCLAW_IMAGE=openclaw-mgx:local
export OPENCLAW_EXTRA_MOUNTS=/data/refdb:/refdb:ro,/data/output:/data/output
# from the OpenClaw repo:
./scripts/docker/setup.sh
```

The gateway user is `node`; conda is `/opt/conda`. Prepend
`/opt/conda/bin` in `tools.exec.pathPrepend` (or rely on
`/etc/profile.d/mgx-conda.sh` inside the image). Plugin install is still
`openclaw plugins install /opt/openclaw-microbiome` (sources are copied into
the image) or a bind-mount of this repo.

Full conda stack is tens of GB. `MGX_ENVS=mgx-base,qiime2-amplicon-2024.10`
limits what the derived image installs.

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
export OPENCLAW_IMAGE=openclaw-mgx:local   # patched + conda; not GHCR
export OPENCLAW_EXTRA_MOUNTS=/data/refdb:/refdb:ro,/data/output:/data/output
# then run openclaw scripts/docker/setup.sh (writes docker-compose.extra.yml)
```

`npm run sync-refs` prints the recommended `OPENCLAW_EXTRA_MOUNTS` string.

`refsMode` only chooses which path namespace is written into
`references.yaml`; it does not perform the mount.

## Plugin config (`openclaw.json`)

`openclaw plugins install` only **installs** the plugin files. You still need
`~/.openclaw/openclaw.json` to **enable** the plugin and set the runtime
options that long 16S / shotgun sessions depend on.

The block below matches a working gateway. Adjust paths to your machine
(jobs, workspace, refs, conda). Restart the gateway after editing.

### Why these settings

| Area | What to set | Why |
|------|-------------|-----|
| **Heartbeat** | `agents.defaults.heartbeat.timeoutSeconds: 43200` (12 hours) | After a background `exec` finishes, OpenClaw often wakes the agent on a heartbeat turn. The default abort is about **10 minutes**. Denoise / taxonomy / phylogeny follow-ups regularly exceed that. |
| **Model HTTP timeout** | `models.providers.*.timeoutSeconds: 300` | The implicit LLM idle/stream watchdog is about **120 seconds**. Slow or tool-heavy replies hit that and surface as `LLM idle timeout`. 300s is the floor used in production here. |
| **Exec wake** | `tools.exec.notifyOnExit` + `notifyOnExitEmptySuccess` | Long CLIs run with `yieldMs` / `timeout: 0`. The agent must wake when the process exits, including when all output went to a log file. |
| **Conda on PATH** | `tools.exec.pathPrepend: ["/opt/conda/bin"]` | The gateway user must see `conda` without `conda activate`. In the `openclaw-mgx` image that path is `/opt/conda/bin`. On a host install, point this at your Miniforge/Miniconda `bin`. |
| **Code Mode off** | `tools.codeMode.enabled: false` | Analysis CLIs go through native `exec` / `read`, not the Code Mode JS sandbox. |
| **No skill workshop** | `tools.deny: ["skill_workshop"]` | Stops the agent from authoring extra skills mid-run that would shadow `plugin-skills/`. |
| **Session memory** | `hooks.internal.entries.session-memory.enabled: true` | Keeps conversation memory hooks on across `/new`, `/reset`, and idle/daily rollover. |
| **Plugin load path** | `plugins.load.paths` | Extra directory OpenClaw searches for the packaged plugin (for example a built `openclaw-microbiome-pkg`). Skip this if you only `openclaw plugins install` from this repo. |

`enabled` / install control **whether** tools and skills appear.
`plugins.entries.microbiome.config.*` control **where** jobs and refs go — they
do not replace the `"skills": ["./skills"]` manifest declaration.

### Microbiome plugin keys

| Key | Meaning |
|-----|---------|
| `enabled` | Load the plugin (tools, skills, `gateway_start`) |
| `jobsRoot` | Analysis jobs root (default `OPENCLAW_JOBS_ROOT` or `./jobs`) |
| `workspaceRoot` | Agent workspace for `.microbiome/session_jobs/` + generated `registry/references.yaml` |
| `refsConfig` | User refs yaml (default `~/.openclaw/microbiome-refs.yaml`) |
| `refsMode` | `auto` / `docker` / `host` for generated `path` values |
| `catalogDir` | Override `catalog/` for tools.yaml |

### Recommended `~/.openclaw/openclaw.json`

Put API keys in OpenClaw **auth profiles** (or the environment), not in a
committed file. The gateway token is read from `OPENCLAW_GATEWAY_TOKEN`.

```json5
{
  agents: {
    defaults: {
      workspace: "/root/.openclaw/workspace",
      // Heartbeat turns after long execs; 12h (default ~10 min will abort them)
      heartbeat: { timeoutSeconds: 43200 }
    },
    entries: {
      main: {
        default: true,
        name: "main",
        workspace: "/root/.openclaw/workspace",
        agentDir: "/root/.openclaw/agents/main/agent",
      },
    },
  },
  gateway: {
    mode: "local",
    port: 16789,
    bind: "lan",
    auth: {
      mode: "token",
      token: { source: "env", provider: "default", id: "OPENCLAW_GATEWAY_TOKEN" },
    },
    controlUi: {
      allowedOrigins: [
        "http://localhost:16789",
        "http://127.0.0.1:16789",
      ],
    },
  },
  tools: {
    codeMode: { enabled: false },
    deny: ["skill_workshop"],
    exec: {
      pathPrepend: ["/opt/conda/bin"],
      notifyOnExit: true,
      notifyOnExitEmptySuccess: true,
    },
  },
  plugins: {
    load: {
      // omit if the plugin was installed with `openclaw plugins install`
      paths: ["/opt/openclaw-microbiome-pkg"],
    },
    entries: {
      microbiome: {
        enabled: true,
        config: {
          jobsRoot: "/root/.openclaw/jobs",
          workspaceRoot: "/root/.openclaw/workspace",
          refsConfig: "/root/.openclaw/microbiome-refs.yaml",
          refsMode: "host", // docker image → container paths; use host on bare metal
        },
      }
    },
  },
  hooks: {
    internal: {
      entries: {
        "session-memory": { enabled: true },
      },
    },
  },
}
```

Also declare each provider’s models and auth profiles the way OpenClaw
normally expects (`models.providers.<id>.models`, `auth.profiles`). The
snippet above only shows the **timeouts and wiring** this plugin needs.

## Gateway startup (bare-metal)

`exec` uses the gateway’s `SHELL`; if unset it falls back to `sh` (often
**dash**), where `source` / bashisms fail. Start with bash; keep analysis on
`conda run` (`CODING.md`), not `conda activate`.

```bash
export SHELL=/bin/bash   # avoid dash as exec shell
export OPENCLAW_GATEWAY_TOKEN=…   # must match gateway.auth.token.id
cd /path/to/openclaw
node openclaw.mjs gateway --port 16789 --verbose
```

Analysis skills live in **`plugin-skills/`** (`$OPENCLAW_STATE_DIR/plugin-skills`),
not `workspace/skills/`. Keep `workspace/skills/` absent (or empty) so workshop
skills cannot shadow plugin procedures.

Long CLIs: background `exec` + `timeout: 0` + exit wake (`CODING.md`).
See [Exec](https://docs.openclaw.ai/tools/exec) /
[Background](https://docs.openclaw.ai/gateway/background-process).

## Session job

```text
mgx_create_job (per OpenClaw conversation / sessionKey)
  → reuse OPENCLAW_SESSION_JOB_ID
  → else reuse .microbiome/session_jobs/<sessionKey>
  → else create jobsRoot/<YYYYMMDD-HHMMSS-hex>/
       stage/  analysis/  reproducibility/
  → write .microbiome/session_jobs/<sessionKey>
```

Different conversations get different job directories. All analysis artifacts for
a conversation stay under that conversation’s job directory.

## Skills (index)

| Area | Skills |
|------|--------|
| 16S | `16s-import` → `16s-denoise-dada2` → `16s-feature-summarize` → `16s-taxonomy` → `16s-phylogeny` → `16s-diversity` → optional `16s-export` / `16s-picrust2` |
| Shotgun | `shotgun-kneaddata` → `shotgun-metaphlan` → optional `shotgun-humann` / `shotgun-gene-catalog` / `shotgun-eggnog` / `shotgun-vfdb` / `shotgun-rgi` / `shotgun-bakta` / `shotgun-gapseq` / `shotgun-gutsmash` / `shotgun-antismash` / `shotgun-aviary` |
| Public data | `sra-search`, `ncbi-assembly-proteins` |
| Stats / REST | `stats-*`, `annotation-*` |

## Local check

```bash
npm test
npm run build
npm run sync-refs -- --refs examples/microbiome-refs.yaml --workspace ./workspace --mode docker
npm run dry-run
```
