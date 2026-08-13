#!/usr/bin/env bash
# Build openclaw:patched from the patch-pack pin, then openclaw-mgx:local
# (patched gateway + all conda runtimes).
#
# Does not modify your OpenClaw checkout: patches are applied in a throwaway
# git worktree at the pinned commit.
set -euo pipefail

SCRIPT_DIR=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)
ROOT=$(cd "${SCRIPT_DIR}/.." && pwd)
MANIFEST="${ROOT}/patches/openclaw-exec-session-wake/manifest.json"
APPLY="${ROOT}/patches/openclaw-exec-session-wake/scripts/apply-openclaw-patches.sh"
OPENCLAW_ROOT=${OPENCLAW_ROOT:-}
OPENCLAW_PATCHED_IMAGE=${OPENCLAW_PATCHED_IMAGE:-openclaw:patched}
MGX_IMAGE=${MGX_IMAGE:-openclaw-mgx:local}
MGX_ENVS=${MGX_ENVS:-all}
SKIP_CONDA=0
WORKTREE=""

usage() {
  cat <<'EOF'
Usage: build-openclaw-mgx-image.sh [--root DIR] [--skip-conda]

  --root DIR      OpenClaw git checkout (default: OPENCLAW_ROOT or ../openclaw)
  --skip-conda    Only build openclaw:patched (no mgx-base / QIIME / bioBakery)

Env:
  OPENCLAW_PATCHED_IMAGE  default openclaw:patched
  MGX_IMAGE               default openclaw-mgx:local
  MGX_ENVS                default all  (or comma list, passed to bootstrap)
EOF
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    --root) OPENCLAW_ROOT=$2; shift 2 ;;
    --skip-conda) SKIP_CONDA=1; shift ;;
    -h|--help) usage; exit 0 ;;
    *)
      echo "unknown arg: $1" >&2
      usage >&2
      exit 2
      ;;
  esac
done

if [[ -z "$OPENCLAW_ROOT" ]]; then
  if [[ -d "${ROOT}/../openclaw" ]]; then
    OPENCLAW_ROOT=$(cd "${ROOT}/../openclaw" && pwd)
  else
    echo "Set OPENCLAW_ROOT or pass --root" >&2
    exit 2
  fi
fi

if [[ ! -d "${OPENCLAW_ROOT}/.git" ]]; then
  echo "OpenClaw root must be a git checkout: ${OPENCLAW_ROOT}" >&2
  exit 1
fi

if [[ ! -x "$APPLY" ]]; then
  echo "missing patch helper: ${APPLY}" >&2
  exit 1
fi

PIN=$(python3 -c "import json; print(json.load(open('${MANIFEST}'))['target']['gitCommit'])")
PIN_SHORT=$(python3 -c "import json; print(json.load(open('${MANIFEST}'))['target']['gitCommitShort'])")

echo "==> OpenClaw pin check"
set +e
"${ROOT}/scripts/check-openclaw-pin.sh" --root "$OPENCLAW_ROOT"
pin_rc=$?
set -e
if [[ "$pin_rc" -eq 2 ]]; then
  echo "Cannot build: pin commit ${PIN} is not in ${OPENCLAW_ROOT}" >&2
  echo "  git -C ${OPENCLAW_ROOT} fetch origin ${PIN}" >&2
  exit 1
fi

cleanup() {
  if [[ -n "$WORKTREE" && -d "$WORKTREE" ]]; then
    git -C "$OPENCLAW_ROOT" worktree remove --force "$WORKTREE" >/dev/null 2>&1 || true
    rm -rf "$WORKTREE"
  fi
}
trap cleanup EXIT

WORKTREE=$(mktemp -d "${TMPDIR:-/tmp}/openclaw-mgx-build.XXXXXX")
rmdir "$WORKTREE"
echo "==> worktree at pin ${PIN_SHORT}"
git -C "$OPENCLAW_ROOT" worktree add --detach "$WORKTREE" "$PIN"

echo "==> applying patches in worktree"
"$APPLY" --apply --root "$WORKTREE"

export DOCKER_BUILDKIT=1
BUILD_TIMESTAMP=$(date -u +%Y-%m-%dT%H:%M:%SZ)
echo "==> docker build ${OPENCLAW_PATCHED_IMAGE}"
docker build \
  --build-arg "GIT_COMMIT=${PIN}" \
  --build-arg "OPENCLAW_BUILD_TIMESTAMP=${BUILD_TIMESTAMP}" \
  -t "$OPENCLAW_PATCHED_IMAGE" \
  -f "${WORKTREE}/Dockerfile" \
  "$WORKTREE"

if [[ "$SKIP_CONDA" -eq 1 ]]; then
  echo "OK ${OPENCLAW_PATCHED_IMAGE} (--skip-conda)"
  echo "Deploy: export OPENCLAW_IMAGE=${OPENCLAW_PATCHED_IMAGE}"
  exit 0
fi

echo "==> docker build ${MGX_IMAGE} (conda envs: ${MGX_ENVS})"
docker build \
  --build-arg "OPENCLAW_IMAGE=${OPENCLAW_PATCHED_IMAGE}" \
  --build-arg "MGX_ENVS=${MGX_ENVS}" \
  -t "$MGX_IMAGE" \
  -f "${ROOT}/docker/Dockerfile" \
  "$ROOT"

echo "OK ${MGX_IMAGE}"
echo "Deploy with OpenClaw compose:"
echo "  export OPENCLAW_IMAGE=${MGX_IMAGE}"
echo "  export OPENCLAW_EXTRA_MOUNTS=/data/refdb:/refdb:ro,/data/output:/data/output"
echo "  (cd ${OPENCLAW_ROOT} && ./scripts/docker/setup.sh)"
