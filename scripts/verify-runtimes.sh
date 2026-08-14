#!/usr/bin/env bash
# Check conda envs from runtimes.yaml actually provide their primary CLIs.
set -euo pipefail

PREFIX="${CONDA_ROOT:-}"
if [[ -z "$PREFIX" ]]; then
  if command -v conda >/dev/null 2>&1; then
    PREFIX=$(conda info --base)
  elif [[ -x /opt/conda/bin/conda ]]; then
    PREFIX=/opt/conda
  else
    echo "conda not found (set CONDA_ROOT)" >&2
    exit 1
  fi
fi
CONDA_BIN="${PREFIX}/bin/conda"
if [[ ! -x "$CONDA_BIN" ]]; then
  echo "conda executable not found at ${CONDA_BIN}" >&2
  exit 1
fi

export PATH="${PREFIX}/bin:${PATH}"

check_cli() {
  local env=$1 cli=$2
  if [[ ! -d "${PREFIX}/envs/${env}" ]]; then
    echo "MISSING env: ${env}"
    return 1
  fi
  if "$CONDA_BIN" run -n "$env" --no-capture-output which "$cli" >/dev/null 2>&1 \
    || "$CONDA_BIN" run -n "$env" --no-capture-output command -v "$cli" >/dev/null 2>&1; then
    echo "OK  ${env}  ${cli}"
    return 0
  fi
  echo "MISSING cli: ${env} → ${cli}"
  return 1
}

check_r_pkg() {
  local env=$1 pkg=$2
  if [[ ! -d "${PREFIX}/envs/${env}" ]]; then
    echo "MISSING env: ${env}"
    return 1
  fi
  if "$CONDA_BIN" run -n "$env" --no-capture-output Rscript -e "quit(status=as.integer(!requireNamespace('${pkg}', quietly=TRUE)))" >/dev/null 2>&1; then
    echo "OK  ${env}  R:${pkg}"
    return 0
  fi
  echo "MISSING R pkg: ${env} → ${pkg}"
  return 1
}

failed=0
check_cli qiime2-amplicon-2024.10 qiime || failed=1
check_cli picrust2 picrust2_pipeline.py || failed=1
check_cli biobakery_workflows kneaddata || failed=1
check_cli biobakery_workflows metaphlan || failed=1
check_cli biobakery_workflows humann || failed=1
check_cli eggnog_mapper emapper.py || failed=1
check_cli eggnog_mapper prodigal || failed=1
check_cli rgi rgi || failed=1
check_cli aviary aviary || failed=1
check_cli bakta bakta || failed=1
check_cli mgx-base python || failed=1
check_cli mgx-base Rscript || failed=1
check_cli mgx-base seqtk || failed=1
check_cli mgx-base samtools || failed=1
check_cli mgx-base cd-hit || failed=1
check_r_pkg mgx-base maaslin3 || failed=1
check_r_pkg mgx-base DESeq2 || failed=1

if [[ "$failed" -ne 0 ]]; then
  echo "verify failed" >&2
  exit 1
fi
echo "OK verify-runtimes"
