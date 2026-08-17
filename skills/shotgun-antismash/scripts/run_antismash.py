#!/usr/bin/env python3
"""Reference helper: official antiSMASH 8 on a genome sequence.

Resolve antismash_db via registry/references.yaml. Never download databases.

Example:
  export ANTISMASH_DB=/refdb/antiSMASH_db/databases
  python run_antismash.py \\
    --sequence /path/to/genome.gbk \\
    --output-dir /path/to/job/analysis/shotgun-antismash \\
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
    taxon: str,
    genefinding: str | None,
    extra: list[str],
) -> Path:
    output_dir.parent.mkdir(parents=True, exist_ok=True)
    sequence = _require_file(sequence, "input sequence")
    databases = _require_dir(databases, "antiSMASH --databases")
    cmd = [
        "conda",
        "run",
        "--no-capture-output",
        "-n",
        conda_env,
        "antismash",
        "--databases",
        str(databases),
        "--output-dir",
        str(output_dir),
        "--cpus",
        str(threads),
        "--taxon",
        taxon,
    ]
    if genefinding:
        cmd.extend(["--genefinding-tool", genefinding])
    cmd.extend(extra)
    cmd.append(str(sequence))
    print("Running:", " ".join(cmd), flush=True)
    subprocess.run(cmd, check=True)
    return output_dir


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--sequence", type=Path, required=True)
    p.add_argument("--output-dir", type=Path, required=True)
    p.add_argument("--threads", type=int, default=8)
    p.add_argument("--taxon", default="bacteria", choices=("bacteria", "fungi"))
    p.add_argument(
        "--genefinding-tool",
        default=None,
        help="Default prodigal when the input is not GenBank/EMBL",
    )
    p.add_argument("--conda-env", default=os.environ.get("CONDA_ENV_ANTISMASH", "antismash"))
    p.add_argument(
        "--databases",
        type=Path,
        default=Path(os.environ["ANTISMASH_DB"]) if os.environ.get("ANTISMASH_DB") else None,
    )
    args, extra = p.parse_known_args()
    if args.databases is None:
        raise SystemExit(
            "Need --databases or ANTISMASH_DB (registry/references.yaml antismash_db.path)."
        )
    genefinding = args.genefinding_tool
    suffix = args.sequence.suffix.lower()
    if genefinding is None and suffix not in {".gbk", ".gb", ".gbff", ".embl", ".emb"}:
        genefinding = "prodigal"
    out = run(
        args.sequence,
        args.output_dir,
        threads=args.threads,
        conda_env=args.conda_env,
        databases=args.databases,
        taxon=args.taxon,
        genefinding=genefinding,
        extra=extra,
    )
    print(f"antismash: {out}")


if __name__ == "__main__":
    try:
        main()
    except subprocess.CalledProcessError as e:
        sys.exit(e.returncode)
