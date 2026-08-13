# Images

Agent-facing tool mapping is still [`../workspace/registry/runtimes.yaml`](../workspace/registry/runtimes.yaml)
(`conda_env` + `tools` only). Do not put install recipes there.

To bake a **patched OpenClaw gateway + all conda envs** into one image:

```bash
./scripts/check-openclaw-pin.sh
./scripts/build-openclaw-mgx-image.sh
# tags: openclaw:patched  then  openclaw-mgx:local
```

That script does **not** use `ghcr.io/openclaw/openclaw`. It checks out the
patch-pack pin in a throwaway worktree, applies `patches/openclaw-exec-session-wake`,
builds OpenClaw’s own Dockerfile from that tree, then [`../docker/Dockerfile`](../docker/Dockerfile)
installs Miniforge + `environments/*.yml`.

Host-only conda (no gateway image):

```bash
./scripts/bootstrap-runtimes.sh --all
./scripts/verify-runtimes.sh
```
