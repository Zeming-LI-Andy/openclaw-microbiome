#!/usr/bin/env bash
# Apply / reverse / check the openclaw-exec-session-wake patch series.
set -euo pipefail

SCRIPT_DIR=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)
PATCH_DIR=$(cd "${SCRIPT_DIR}/.." && pwd)
OPENCLAW_ROOT=${OPENCLAW_ROOT:-/app/microclaw/openclaw}
MODE=apply

usage() {
  cat <<'EOF'
Usage: apply-openclaw-patches.sh [--check|--reverse|--apply] [--root DIR]

  --check     git apply --check only (default dry verification)
  --reverse   reverse the series (last → first)
  --apply     apply the series (default)
  --root DIR  OpenClaw checkout (default: OPENCLAW_ROOT or /app/microclaw/openclaw)

Environment:
  OPENCLAW_ROOT   Override OpenClaw checkout path
EOF
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    --check) MODE=check; shift ;;
    --reverse) MODE=reverse; shift ;;
    --apply) MODE=apply; shift ;;
    --root)
      OPENCLAW_ROOT=$2
      shift 2
      ;;
    -h|--help) usage; exit 0 ;;
    *)
      echo "unknown arg: $1" >&2
      usage >&2
      exit 2
      ;;
  esac
done

if [[ ! -d "${OPENCLAW_ROOT}/.git" && ! -f "${OPENCLAW_ROOT}/package.json" ]]; then
  echo "OpenClaw root does not look valid: ${OPENCLAW_ROOT}" >&2
  exit 1
fi

if [[ ! -f "${PATCH_DIR}/series" || ! -f "${PATCH_DIR}/manifest.json" ]]; then
  echo "patch pack incomplete under ${PATCH_DIR}" >&2
  exit 1
fi

echo "OpenClaw root : ${OPENCLAW_ROOT}"
if [[ -f "${OPENCLAW_ROOT}/package.json" ]]; then
  python3 - <<PY
import json
from pathlib import Path
pkg = json.loads(Path("${OPENCLAW_ROOT}/package.json").read_text())
man = json.loads(Path("${PATCH_DIR}/manifest.json").read_text())
target = man["target"]
print(f"package.json  : {pkg.get('name')}@{pkg.get('version')}")
print(f"patch targets : openclaw@{target['version']} @ {target['gitCommitShort']}")
if str(pkg.get("version")) != str(target.get("version")):
    print("WARNING: package.json version differs from patch target version.")
PY
fi
if [[ -d "${OPENCLAW_ROOT}/.git" ]]; then
  (
    cd "${OPENCLAW_ROOT}"
    echo "git HEAD      : $(git rev-parse HEAD)"
    TARGET=$(python3 -c "import json; print(json.load(open('${PATCH_DIR}/manifest.json'))['target']['gitCommit'])")
    if [[ "$(git rev-parse HEAD)" != "${TARGET}" ]]; then
      echo "WARNING: HEAD differs from patch target commit ${TARGET}"
      echo "         Rebase/retest before relying on this apply."
    else
      echo "git HEAD matches patch target commit."
    fi
  )
fi

PATCHES=()
while IFS= read -r line || [[ -n "$line" ]]; do
  case "$line" in
    ''|\#*) continue ;;
    *) PATCHES+=("$line") ;;
  esac
done < "${PATCH_DIR}/series"
if [[ ${#PATCHES[@]} -eq 0 ]]; then
  echo "empty series" >&2
  exit 1
fi

if [[ "${MODE}" == "reverse" ]]; then
  reversed=()
  i=${#PATCHES[@]}
  while [[ "$i" -gt 0 ]]; do
    i=$((i - 1))
    reversed+=("${PATCHES[$i]}")
  done
  PATCHES=("${reversed[@]}")
fi

# --check must validate the series in order. Independently checking each file
# against a clean tree falsely accepts later patches that only apply after earlier ones.
status=0
applied_for_check=()
for patch in "${PATCHES[@]}"; do
  file="${PATCH_DIR}/${patch}"
  if [[ ! -f "${file}" ]]; then
    echo "missing patch: ${file}" >&2
    exit 1
  fi
  args=(apply --whitespace=nowarn)
  case "${MODE}" in
    check) args+=(--check) ;;
    reverse) args+=(-R) ;;
    apply) ;;
  esac
  echo "==> git ${args[*]} ${patch}"
  if ! git -C "${OPENCLAW_ROOT}" "${args[@]}" "${file}"; then
    echo "FAILED: ${patch}" >&2
    status=1
    break
  fi
  if [[ "${MODE}" == "check" ]]; then
    # Apply so the next patch is checked against the cumulative series state.
    if ! git -C "${OPENCLAW_ROOT}" apply --whitespace=nowarn "${file}"; then
      echo "FAILED: apply after check ${patch}" >&2
      status=1
      break
    fi
    applied_for_check+=("${file}")
  fi
done

if [[ "${MODE}" == "check" && ${#applied_for_check[@]} -gt 0 ]]; then
  echo "==> reversing temporary check applies (${#applied_for_check[@]} patch(es))"
  for ((i=${#applied_for_check[@]}-1; i>=0; i--)); do
    git -C "${OPENCLAW_ROOT}" apply --whitespace=nowarn -R "${applied_for_check[$i]}" || true
  done
fi

if [[ ${status} -eq 0 ]]; then
  echo "OK (${MODE}) ${#PATCHES[@]} patch(es)"
else
  echo "FAILED (${MODE})" >&2
fi
exit "${status}"
