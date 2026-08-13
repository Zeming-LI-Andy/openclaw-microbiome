#!/usr/bin/env bash
# Compare an OpenClaw checkout to patches/openclaw-exec-session-wake/manifest.json.
# Exit 0 if HEAD == pin, 2 if pin is missing, 1 if HEAD differs (pin still present).
set -euo pipefail

SCRIPT_DIR=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)
ROOT=$(cd "${SCRIPT_DIR}/.." && pwd)
MANIFEST="${ROOT}/patches/openclaw-exec-session-wake/manifest.json"
OPENCLAW_ROOT=${OPENCLAW_ROOT:-}

usage() {
  cat <<'EOF'
Usage: check-openclaw-pin.sh [--root DIR]

  --root DIR   OpenClaw checkout (default: OPENCLAW_ROOT or ../openclaw)

Prints package version + git commit vs the patch pack pin.
EOF
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    --root) OPENCLAW_ROOT=$2; shift 2 ;;
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

if [[ ! -f "${OPENCLAW_ROOT}/package.json" ]]; then
  echo "Not an OpenClaw checkout: ${OPENCLAW_ROOT}" >&2
  exit 2
fi

python3 - "$OPENCLAW_ROOT" "$MANIFEST" <<'PY'
import json
import subprocess
import sys
from pathlib import Path

root = Path(sys.argv[1])
man = json.loads(Path(sys.argv[2]).read_text())
pkg = json.loads((root / "package.json").read_text())
target = man["target"]
pin = target["gitCommit"]
head = subprocess.check_output(["git", "-C", str(root), "rev-parse", "HEAD"], text=True).strip()
pin_ok = subprocess.call(["git", "-C", str(root), "cat-file", "-t", pin], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL) == 0

print(f"OpenClaw root     : {root}")
print(f"package.json      : {pkg.get('name')}@{pkg.get('version')}")
print(f"git HEAD          : {head}")
print(f"patch pack        : {man['id']}")
print(f"patch target      : openclaw@{target['version']} @ {target['gitCommitShort']}")
print(f"patch commit      : {pin}")
if pkg.get("version") != target.get("version"):
    print("VERSION MISMATCH  : package.json version != patch target version")
else:
    print("VERSION MATCH     : package.json version == patch target version")

if not pin_ok:
    print("PIN MISSING       : fetch the pin commit before building the image")
    sys.exit(2)

if head == pin:
    print("COMMIT MATCH      : HEAD is the patch pin (safe to apply in place)")
    sys.exit(0)

print("COMMIT MISMATCH   : HEAD is not the pin")
print("                   build-openclaw-mgx-image.sh uses a worktree at the pin")
print("                   and does not modify this checkout.")
sys.exit(1)
PY
