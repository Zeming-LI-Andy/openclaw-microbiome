# Patch: openclaw-exec-session-wake

External OpenClaw patch pack for **reliable background `exec` → session wake**
on dashboard / webchat (and other `deliverToUser=false` targets).

Do **not** keep these changes only as dirty edits under `openclaw/`.
Apply this pack to a pinned OpenClaw checkout, then build/restart the gateway.

## Target OpenClaw version

| Field | Value |
|-------|-------|
| Package | `openclaw` |
| Version | **`2026.7.2`** |
| Git commit | `35c9c76b8c76c5d79f8f06b4bdce982518e61449` |
| Commit date | 2026-08-03T04:52:52-07:00 |
| Upstream tip subject | `fix(otel): fail closed when configured TLS material is invalid (#118648)` |

Canonical machine-readable pin: [`manifest.json`](./manifest.json).

If your OpenClaw commit differs, run a dry-apply first and expect hunks to need
rebase:

```bash
./scripts/apply-openclaw-patches.sh --check
```

## What it fixes

1. **`0001-session-continue-exec-event-prompt.patch`**  
   When outbound delivery is disabled, exec-completion heartbeats no longer force
   silent `HEARTBEAT_OK only`. The session gets the completion text and is told to
   continue in-session (still no external channel relay).

2. **`0002-clear-disposed-transcript-als-on-exec-wake.patch`**  
   Background exec exit / heartbeat wake clears a disposed attempt’s transcript
   write ALS (same pattern as subagent/media wakes), so `admitUserTurn` can start
   an agent run instead of failing with
   `attempt disposed before transcript write`.

3. **`0003-exec-notify-immediate-and-steer-wake.patch`**  
   `notifyOnExit` no longer uses `intent: "event"` (agent `nextDueMs` could delay
   dashboard wakes for minutes). Idle sessions wake with `intent: "immediate"`;
   if the target session already has an active run, completion is **steered into
   that turn** (fallback to immediate heartbeat if steer cannot queue).

4. **`0004-tool-guidance-yield-before-poll.patch`**  
   Model-facing yield/handoff guidance in one place: `yieldMs` vs immediate
   `background: true`, running-exec responses point to `sessions_yield` (not
   poll), and `sessions_yield` covers subagent and background exec events.

## Apply

From this directory, or via the helper (default OpenClaw root:
`/app/microclaw/openclaw`):

```bash
# dry-run
./scripts/apply-openclaw-patches.sh --check

# apply
./scripts/apply-openclaw-patches.sh

# reverse
./scripts/apply-openclaw-patches.sh --reverse
```

Override the tree:

```bash
OPENCLAW_ROOT=/path/to/openclaw ./scripts/apply-openclaw-patches.sh
```

After apply: rebuild OpenClaw (`pnpm` / `node scripts/tsdown-build.mjs` as you
usually do) and restart the gateway.

## Series

See [`series`](./series) for apply order.

## Why this lives outside OpenClaw

Microbiome long steps rely on **background exec + `notifyOnExit` wake**
(`workspace/CODING.md`). These upstream fixes are carried as a versioned patch
pack so the OpenClaw checkout can stay clean / upgradable, with an explicit
version pin for support and rebases.
