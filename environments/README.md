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
#   biobakery.yml             → biobakery_workflows
#   aviary.yml                → aviary
#   qiime2-amplicon.yml       → qiime2-amplicon-2024.10 (official distro URL)
#
# Host:
#   ./scripts/bootstrap-runtimes.sh --all
#   ./scripts/verify-runtimes.sh
#
# Docker (patched OpenClaw + these envs):
#   ./scripts/build-openclaw-mgx-image.sh
#
# Reference DBs are not installed here — use ~/.openclaw/microbiome-refs.yaml.
