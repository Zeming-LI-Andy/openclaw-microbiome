# Conda env recipes for openclaw-microbiome.
#
# These files are for operators / Docker. Analysis agents read
# workspace/registry/runtimes.yaml (allowlist + conda_env names) and must not
# conda install during a job.
#
# Env directory names must match runtimes.yaml `conda_env`:
#
#   mgx-base.yml              → mgx-base  (stats + host)
#   picrust2.yml              → picrust2
#   eggnog_mapper.yml         → eggnog_mapper
#   rgi.yml                   → rgi
#   bakta.yml                 → bakta
#   gapseq.yml                → gapseq
#   gutsmash.yml              → gutsmash
#   antismash.yml             → antismash
#   biobakery.yml             → biobakery_workflows
#   aviary.yml                → aviary
#   qiime2-amplicon.yml       → qiime2-amplicon-2024.10 (official distro URL)
#
# Top-level package versions are pinned to a known-good linux-64 solve.
# QIIME 2 is pinned by the official 2024.10 distro YAML URL, not a local list.
#
# Host:
#   ./scripts/bootstrap-runtimes.sh --all --refdb /path/to/Metagenome_profiling
#   ./scripts/verify-runtimes.sh
#
# Docker (patched OpenClaw + these envs):
#   ./scripts/build-openclaw-mgx-image.sh
#   bootstrap defaults --refdb to /refdb (OPENCLAW_EXTRA_MOUNTS=...:/refdb:ro).
#
# Reference DBs are not downloaded here. bootstrap may symlink / set conda
# activate.d vars so a missing CLI flag still hits /refdb instead of
# auto-downloading (MetaPhlAn, gapseq) or falling back to DEMO (HUMAnN).
