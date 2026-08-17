#!/usr/bin/env python3
"""Reference helper: gutSMASH on a genome sequence.

Resolve gutsmash_db via registry/references.yaml. Never download databases.

Example:
  export GUTSMASH_DB=/refdb/gutsmash/databases
  python run_gutsmash.py \\
    --sequence /path/to/genome.fna \\
    --output-dir /path/to/job/analysis/shotgun-gutsmash \\
    --threads 8
"""

from __future__ import annotations

import argparse
import os
import subprocess
import sys
from pathlib import Path


def _require_file(path: Path, label: str) -> Path:
    if not path.is_file():
        raise FileNotFoundError(f"{label} not found: {path}")
    return path


def _require_dir(path: Path, label: str) -> Path:
    if not path.is_dir():
        raise FileNotFoundError(f"{label} not found: {path}")
    return path


def run(
    sequence: Path,
    output_dir: Path,
    *,
    threads: int,
    conda_env: str,
    databases: Path,
    genefinding: str,
    extra: list[str],
) -> Path:
    output_dir.parent.mkdir(parents=True, exist_ok=True)
    sequence = _require_file(sequence, "input sequence")
    databases = _require_dir(databases, "gutSMASH --databases")
    cmd = [
        "conda",
        "run",
        "--no-capture-output",
        "-n",
        conda_env,
        "gutsmash",
        "--databases",
        str(databases),
        "--output-dir",
        str(output_dir),
        "--cpus",
        str(threads),
        "--genefinding-tool",
        genefinding,
        *extra,
        str(sequence),
    ]
    print("Running:", " ".join(cmd), flush=True)
    subprocess.run(cmd, check=True)
    return output_dir


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--sequence", type=Path, required=True)
    p.add_argument("--output-dir", type=Path, required=True)
    p.add_argument("--threads", type=int, default=8)
    p.add_argument(
        "--genefinding-tool",
        default="prodigal",
        help="Use none when CDS are already annotated",
    )
    p.add_argument("--conda-env", default=os.environ.get("CONDA_ENV_GUTSMASH", "gutsmash"))
    p.add_argument(
        "--databases",
        type=Path,
        default=Path(os.environ["GUTSMASH_DB"]) if os.environ.get("GUTSMASH_DB") else None,
    )
    args, extra = p.parse_known_args()
    if args.databases is None:
        raise SystemExit(
            "Need --databases or GUTSMASH_DB (registry/references.yaml gutsmash_db.path)."
        )
    out = run(
        args.sequence,
        args.output_dir,
        threads=args.threads,
        conda_env=args.conda_env,
        databases=args.databases,
        genefinding=args.genefinding_tool,
        extra=extra,
    )
    print(f"gutsmash: {out}")


if __name__ == "__main__":
    try:
        main()
    except subprocess.CalledProcessError as e:
        sys.exit(e.returncode)
