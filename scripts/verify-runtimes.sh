#!/usr/bin/env bash
# Check conda envs from runtimes.yaml actually provide their primary CLIs.
# Aviary also needs pixi plus CPU nested pixi envs from `aviary build`.
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

# Aviary 0.13.2 runs assemblers/binners via pixi envs beside pixi.toml.
check_aviary_nested_envs() {
  local env=aviary
  if [[ ! -d "${PREFIX}/envs/${env}" ]]; then
    echo "MISSING env: ${env}"
    return 1
  fi
  if "$CONDA_BIN" run -n "$env" --no-capture-output python -c '
import pathlib, sys
import aviary
root = pathlib.Path(aviary.__file__).resolve().parent / ".pixi" / "envs"
need = ("gtdbtk", "checkm2", "spades", "eggnog")
if not root.is_dir():
    sys.stderr.write("MISSING aviary pixi envs dir: %s\n" % root)
    sys.exit(1)
missing = [n for n in need if not (root / n).is_dir()]
if missing:
    sys.stderr.write("MISSING aviary pixi env(s): %s\n" % ", ".join(missing))
    sys.exit(1)
'; then
    echo "OK  ${env}  pixi nested envs"
    return 0
  fi
  echo "MISSING aviary nested pixi envs (bootstrap runs aviary build)"
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
check_cli aviary pixi || failed=1
check_aviary_nested_envs || failed=1
check_cli bakta bakta || failed=1
check_cli gapseq gapseq || failed=1
check_cli gutsmash gutsmash || failed=1
check_cli antismash antismash || failed=1
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
