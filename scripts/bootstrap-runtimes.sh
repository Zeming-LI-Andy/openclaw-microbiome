#!/usr/bin/env bash
# Create conda envs from environments/*.yml (host or Docker).
# Usage:
#   ./scripts/bootstrap-runtimes.sh --all
#   ./scripts/bootstrap-runtimes.sh --only mgx-base,picrust2
#   CONDA_ROOT=/opt/conda ./scripts/bootstrap-runtimes.sh --all --force
set -euo pipefail

SCRIPT_DIR=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)
ROOT=$(cd "${SCRIPT_DIR}/.." && pwd)
ENV_DIR="${ROOT}/environments"
ONLY=""
FORCE=0
ALL=0
PREFIX="${CONDA_ROOT:-}"

usage() {
  cat <<'EOF'
Usage: bootstrap-runtimes.sh [--all | --only name,name] [--prefix DIR] [--force]

  --all           Create every env in environments/
  --only LIST     Comma-separated conda env names (runtimes.yaml conda_env)
  --prefix DIR    Conda root (default: CONDA_ROOT or `conda info --base`)
  --force         Remove and recreate envs that already exist

Env names:
  mgx-base, qiime2-amplicon-2024.10, picrust2, biobakery_workflows,
  eggnog_mapper, rgi, aviary
EOF
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    --all) ALL=1; shift ;;
    --only) ONLY=$2; shift 2 ;;
    --prefix) PREFIX=$2; shift 2 ;;
    --force) FORCE=1; shift ;;
    -h|--help) usage; exit 0 ;;
    *)
      echo "unknown arg: $1" >&2
      usage >&2
      exit 2
      ;;
  esac
done

if [[ "$ALL" -eq 0 && -z "$ONLY" ]]; then
  usage >&2
  exit 2
fi

conda_platform() {
  local os arch
  os=$(uname -s)
  arch=$(uname -m)
  case "${os}-${arch}" in
    Linux-x86_64) echo linux-64 ;;
    Linux-aarch64|Linux-arm64) echo linux-aarch64 ;;
    Darwin-x86_64) echo osx-64 ;;
    Darwin-arm64) echo osx-arm64 ;;
    *) echo "unsupported-platform:${os}-${arch}" ;;
  esac
}

distro_url_for() {
  local file=$1 platform=$2
  python3 - "$file" "$platform" <<'PY'
import sys
path, platform = sys.argv[1], sys.argv[2]
wanted = None
in_files = False
with open(path) as fh:
    for raw in fh:
        line = raw.rstrip("\n")
        if line.startswith("distro_files:"):
            in_files = True
            continue
        if in_files:
            if line and not line.startswith(" ") and not line.startswith("\t"):
                break
            stripped = line.strip()
            if stripped.startswith(platform + ":"):
                wanted = stripped.split(":", 1)[1].strip()
                break
if not wanted:
    sys.exit(f"no distro_files entry for platform {platform} in {path}")
print(wanted)
PY
}

recipe_for_env() {
  case "$1" in
    mgx-base) echo "${ENV_DIR}/mgx-base.yml" ;;
    picrust2) echo "${ENV_DIR}/picrust2.yml" ;;
    eggnog_mapper) echo "${ENV_DIR}/eggnog_mapper.yml" ;;
    rgi) echo "${ENV_DIR}/rgi.yml" ;;
    biobakery_workflows) echo "${ENV_DIR}/biobakery.yml" ;;
    aviary) echo "${ENV_DIR}/aviary.yml" ;;
    qiime2-amplicon-2024.10) echo "${ENV_DIR}/qiime2-amplicon.yml" ;;
    *) echo "" ;;
  esac
}

ALL_ENVS=(
  mgx-base
  qiime2-amplicon-2024.10
  picrust2
  biobakery_workflows
  eggnog_mapper
  rgi
  aviary
)

resolve_prefix() {
  if [[ -n "$PREFIX" ]]; then
    return 0
  fi
  if command -v conda >/dev/null 2>&1; then
    PREFIX=$(conda info --base)
    return 0
  fi
  if [[ -x /opt/conda/bin/conda ]]; then
    PREFIX=/opt/conda
    return 0
  fi
  echo "No conda found. Install Miniforge/Miniconda and retry, or pass --prefix." >&2
  exit 1
}

resolve_prefix
CONDA_BIN="${PREFIX}/bin/conda"
if [[ ! -x "$CONDA_BIN" ]]; then
  echo "conda executable not found at ${CONDA_BIN}" >&2
  exit 1
fi

if [[ -x "${PREFIX}/bin/mamba" ]]; then
  CREATE_BIN="${PREFIX}/bin/mamba"
else
  CREATE_BIN="$CONDA_BIN"
fi

export PATH="${PREFIX}/bin:${PATH}"

TARGETS=()
if [[ "$ALL" -eq 1 ]]; then
  TARGETS=("${ALL_ENVS[@]}")
else
  IFS=',' read -r -a TARGETS <<< "$ONLY"
fi

is_official_distro() {
  grep -q '^kind: official-distro' "$1"
}

env_exists() {
  local name=$1
  [[ -d "${PREFIX}/envs/${name}" ]]
}

create_env() {
  local name=$1 recipe=$2
  local tmp yml platform url
  if env_exists "$name"; then
    if [[ "$FORCE" -eq 0 ]]; then
      echo "==> skip ${name} (exists; pass --force to recreate)"
      return 0
    fi
    echo "==> removing ${name}"
    "$CONDA_BIN" env remove -y -n "$name"
  fi

  yml=$recipe
  if is_official_distro "$recipe"; then
    platform=$(conda_platform)
    if [[ "$platform" == unsupported-platform:* ]]; then
      echo "QIIME 2 recipe has no mapping for ${platform#unsupported-platform:}" >&2
      return 1
    fi
    url=$(distro_url_for "$recipe" "$platform")
    tmp=$(mktemp)
    echo "==> fetching official distro YAML for ${name} (${platform})"
    echo "    ${url}"
    if command -v curl >/dev/null 2>&1; then
      curl -fsSL "$url" -o "$tmp"
    else
      wget -qO "$tmp" "$url"
    fi
    yml=$tmp
  fi

  echo "==> creating ${name} from ${recipe}"
  if [[ "$CREATE_BIN" == *mamba ]]; then
    "$CREATE_BIN" env create -n "$name" -f "$yml"
  else
    "$CONDA_BIN" env create -n "$name" -f "$yml"
  fi
  if [[ -n "${tmp:-}" && -f "${tmp:-}" ]]; then
    rm -f "$tmp"
  fi
}

failed=0
for name in "${TARGETS[@]}"; do
  name=$(echo "$name" | tr -d '[:space:]')
  [[ -z "$name" ]] && continue
  recipe=$(recipe_for_env "$name")
  if [[ -z "$recipe" || ! -f "$recipe" ]]; then
    echo "unknown env or missing recipe: ${name}" >&2
    failed=1
    continue
  fi
  if ! create_env "$name" "$recipe"; then
    echo "FAILED: ${name}" >&2
    failed=1
  fi
done

if [[ "$failed" -ne 0 ]]; then
  echo "bootstrap finished with errors" >&2
  exit 1
fi
echo "OK bootstrap (${#TARGETS[@]} env(s))"
