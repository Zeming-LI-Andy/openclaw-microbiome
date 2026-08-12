# patches/

Version-pinned **OpenClaw** patch packs carried by this microbiome repo.

| Pack | Target | Purpose |
|------|--------|---------|
| [`openclaw-exec-session-wake/`](./openclaw-exec-session-wake/) | OpenClaw **`2026.7.2`** @ `35c9c76b8c76…` | Background exec wake and model-facing yield guidance |

Each pack has:

- `manifest.json` — exact package version + git commit pin
- `series` + `*.patch` — ordered unified diffs
- `README.md` — human notes
- `scripts/apply-openclaw-patches.sh` — apply / check / reverse

Do not leave equivalent edits as untracked dirty state under `../openclaw`.
