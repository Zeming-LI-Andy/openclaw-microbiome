#!/usr/bin/env bash
# Create conda envs from environments/*.yml (host or Docker).
# Usage:
#   ./scripts/bootstrap-runtimes.sh --all
#   ./scripts/bootstrap-runtimes.sh --only mgx-base,picrust2
#   CONDA_ROOT=/opt/conda ./scripts/bootstrap-runtimes.sh --all --force
#   ./scripts/bootstrap-runtimes.sh --all --refdb /refdb
#
# Never downloads reference DBs. post_create may point env defaults at --refdb
# (container path /refdb, matching microbiome-refs.yaml relative_path).
set -euo pipefail

SCRIPT_DIR=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)
ROOT=$(cd "${SCRIPT_DIR}/.." && pwd)
ENV_DIR="${ROOT}/environments"
ONLY=""
FORCE=0
ALL=0
PREFIX="${CONDA_ROOT:-}"
REFDB_ROOT=""
REFDB_SET=0

usage() {
  cat <<'EOF'
Usage: bootstrap-runtimes.sh [--all | --only name,name] [--prefix DIR] [--force] [--refdb DIR]

  --all           Create every env in environments/
  --only LIST     Comma-separated conda env names (runtimes.yaml conda_env)
  --prefix DIR    Conda root (default: CONDA_ROOT or `conda info --base`)
  --force         Remove and recreate envs that already exist
  --refdb DIR     Root of the reference tree (microbiome-refs.yaml relative_path).
                  Wires env defaults / symlinks; does not download DBs.
                  Default: /refdb in Docker (or if that dir exists).
                  On a host without /refdb, pass this flag or wiring is skipped.

Env names:
  mgx-base, qiime2-amplicon-2024.10, picrust2, biobakery_workflows,
  eggnog_mapper, rgi, aviary, bakta, gapseq, gutsmash, antismash
EOF
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    --all) ALL=1; shift ;;
    --only) ONLY=$2; shift 2 ;;
    --prefix) PREFIX=$2; shift 2 ;;
    --refdb) REFDB_ROOT=$2; REFDB_SET=1; shift 2 ;;
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
    bakta) echo "${ENV_DIR}/bakta.yml" ;;
    gapseq) echo "${ENV_DIR}/gapseq.yml" ;;
    gutsmash) echo "${ENV_DIR}/gutsmash.yml" ;;
    antismash) echo "${ENV_DIR}/antismash.yml" ;;
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
  bakta
  gapseq
  gutsmash
  antismash
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

resolve_refdb() {
  if [[ "$REFDB_SET" -eq 1 ]]; then
    REFDB_ROOT="${REFDB_ROOT%/}"
    echo "==> refdb: ${REFDB_ROOT} (--refdb)"
    return 0
  fi
  if [[ -f /.dockerenv || "${OPENCLAW_STATE_DIR:-}" == "/home/node/.openclaw" || -d /refdb ]]; then
    REFDB_ROOT=/refdb
    echo "==> refdb: /refdb (container default)"
    return 0
  fi
  REFDB_ROOT=""
  echo "==> refdb: skip wiring (pass --refdb DIR; Docker defaults to /refdb)"
}

resolve_refdb

# Write conda activate.d / deactivate.d exports. Args after env name are KEY=VALUE.
write_conda_env_vars() {
  local name=$1 act deact actf deactf kv key
  shift
  act="${PREFIX}/envs/${name}/etc/conda/activate.d"
  deact="${PREFIX}/envs/${name}/etc/conda/deactivate.d"
  mkdir -p "$act" "$deact"
  actf="${act}/mgx-refdb.sh"
  deactf="${deact}/mgx-refdb.sh"
  {
    echo "#!/usr/bin/env bash"
    echo "# Generated by bootstrap-runtimes.sh. Points at --refdb; does not download."
    for kv in "$@"; do
      key=${kv%%=*}
      printf 'export %s=%q\n' "$key" "${kv#*=}"
    done
  } >"$actf"
  {
    echo "#!/usr/bin/env bash"
    for kv in "$@"; do
      echo "unset ${kv%%=*}"
    done
  } >"$deactf"
  chmod +x "$actf" "$deactf"
  echo "==> ${name}: conda activate.d mgx-refdb.sh"
}

# Replace dest with a symlink to target (ok if target does not exist yet).
replace_with_symlink() {
  local dest=$1 target=$2
  mkdir -p "$(dirname "$dest")"
  if [[ -L "$dest" ]]; then
    ln -sfn "$target" "$dest"
    echo "==> symlink ${dest} -> ${target}"
    return 0
  fi
  if [[ -e "$dest" ]]; then
    rm -rf "$dest"
  fi
  ln -sfn "$target" "$dest"
  echo "==> symlink ${dest} -> ${target}"
}

python_module_dir() {
  local name=$1 module=$2
  "$CONDA_BIN" run -n "$name" --no-capture-output python -c \
    "import ${module}, pathlib; print(pathlib.Path(${module}.__file__).resolve().parent)" \
    | tail -n1
}

# Point env defaults at REFDB_ROOT/<relative_path>. Never downloads DBs.
wire_refdb() {
  local name=$1 root pkg seqdir
  [[ -n "$REFDB_ROOT" ]] || return 0
  [[ -d "${PREFIX}/envs/${name}" ]] || return 0
  root=$REFDB_ROOT
  case "$name" in
    bakta)
      write_conda_env_vars bakta "BAKTA_DB=${root}/bakta_db_full/db-v6.0"
      ;;
    biobakery_workflows)
      write_conda_env_vars biobakery_workflows \
        "METAPHLAN_DB_DIR=${root}/metaphlan_databases"
      echo "==> ${name}: humann_config database_folders -> ${root}/humann_databases"
      "$CONDA_BIN" run -n biobakery_workflows --no-capture-output humann_config \
        --update database_folders nucleotide "${root}/humann_databases/chocophlan_v296_201901" || return 1
      "$CONDA_BIN" run -n biobakery_workflows --no-capture-output humann_config \
        --update database_folders protein "${root}/humann_databases/uniref" || return 1
      "$CONDA_BIN" run -n biobakery_workflows --no-capture-output humann_config \
        --update database_folders utility_mapping "${root}/humann_databases/utility_mapping" || return 1
      ;;
    eggnog_mapper)
      write_conda_env_vars eggnog_mapper \
        "EGGNOG_DATA_DIR=${root}/eggnog/eggnog_5.0"
      ;;
    aviary)
      write_conda_env_vars aviary \
        "GTDBTK_DATA_PATH=${root}/aviary_db/gtdb" \
        "CHECKM2DB=${root}/aviary_db/checkm2db" \
        "EGGNOG_DATA_DIR=${root}/aviary_db/eggnog" \
        "SINGLEM_METAPACKAGE_PATH=${root}/aviary_db/singlem"
      ;;
    gapseq)
      seqdir="${PREFIX}/envs/gapseq/share/gapseq/dat/seq"
      if [[ ! -d "$seqdir" ]]; then
        echo "gapseq dat/seq missing: ${seqdir}" >&2
        return 1
      fi
      replace_with_symlink "${seqdir}/Bacteria" "${root}/gapseq_db/dat/seq/Bacteria"
      replace_with_symlink "${seqdir}/Archaea" "${root}/gapseq_db/dat/seq/Archaea"
      ;;
    antismash)
      pkg=$(python_module_dir antismash antismash) || return 1
      replace_with_symlink "${pkg}/databases" "${root}/antiSMASH_db/databases"
      ;;
    gutsmash)
      pkg=$(python_module_dir gutsmash antismash) || return 1
      replace_with_symlink "${pkg}/databases" "${root}/gutsmash/databases"
      ;;
    *)
      return 0
      ;;
  esac
}

TARGETS=()
if [[ "$ALL" -eq 1 ]]; then
  TARGETS=("${ALL_ENVS[@]}")
else
  IFS=',' read -r -a TARGETS <<< "$ONLY"
fi

is_official_distro() {
  grep -q '^kind: official-distro' "$1"
}

# QIIME 2 / bioBakery mix conda-forge + bioconda (+ extra channels).
# Global channel_priority:strict makes sortmerna/deblur (and similar) unsatisfiable.
needs_flexible_priority() {
  is_official_distro "$1" && return 0
  grep -Eq '^#?[[:space:]]*channel_priority:[[:space:]]*flexible' "$1"
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
    # mamba/conda require .yml/.yaml/.txt; plain mktemp has no suffix.
    tmp=$(mktemp "${TMPDIR:-/tmp}/mgx-distro.XXXXXX")
    mv "$tmp" "${tmp}.yml"
    tmp="${tmp}.yml"
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
  local restore_priority="" rc=0
  if needs_flexible_priority "$recipe"; then
    restore_priority=$("$CONDA_BIN" config --show channel_priority | awk '{print $2}')
    echo "==> channel_priority flexible for ${name} (was ${restore_priority:-unset})"
    "$CONDA_BIN" config --system --set channel_priority flexible
  fi
  if [[ "$CREATE_BIN" == *mamba ]]; then
    "$CREATE_BIN" env create -n "$name" -f "$yml" || rc=$?
  else
    "$CONDA_BIN" env create -n "$name" -f "$yml" || rc=$?
  fi
  if [[ -n "$restore_priority" ]]; then
    "$CONDA_BIN" config --system --set channel_priority "$restore_priority"
  fi
  if [[ -n "${tmp:-}" && -f "${tmp:-}" ]]; then
    rm -f "$tmp"
  fi
  return "$rc"
}

# Extra steps after conda env create. Never download reference DBs here.
post_create() {
  local name=$1 bindir
  case "$name" in
    gutsmash)
      # Pinned to the commit that installed as gutsmash==2.0.1 in mgx-env-test.
      echo "==> pip install gutsmash from git (--no-deps; skip download-antismash-databases)"
      "$CONDA_BIN" run -n gutsmash --no-capture-output pip install --no-deps \
        "git+https://github.com/victoriapascal/gutsmash.git@1651919f7e93d09a995ea080a3c029be84ee48c6" || return 1
      bindir="${PREFIX}/envs/gutsmash/bin"
      if [[ -x "${bindir}/antismash" && ! -e "${bindir}/gutsmash" ]]; then
        ln -s antismash "${bindir}/gutsmash"
      fi
      # gutsmash 2.0.1 uses dict[str, ...] without future annotations; py3.7 needs this.
      echo "==> patching PEP 585 hints for python 3.7"
      "$CONDA_BIN" run -n gutsmash --no-capture-output python -c '
import pathlib, sysconfig
root = pathlib.Path(sysconfig.get_path("purelib")) / "antismash"
needle = "from __future__ import annotations\n"
for path in root.rglob("*.py"):
    text = path.read_text(encoding="utf-8")
    if needle.strip() in text:
        continue
    if "dict[" not in text and "list[" not in text and "tuple[" not in text:
        continue
    path.write_text(needle + text, encoding="utf-8")
    print("patched", path)
'
      ;;
  esac
  wire_refdb "$name" || return 1
  return 0
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
    continue
  fi
  if ! post_create "$name"; then
    echo "FAILED post-create: ${name}" >&2
    failed=1
  fi
done

if [[ "$failed" -ne 0 ]]; then
  echo "bootstrap finished with errors" >&2
  exit 1
fi
echo "OK bootstrap (${#TARGETS[@]} env(s))"
