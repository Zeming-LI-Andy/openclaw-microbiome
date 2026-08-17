#!/usr/bin/env python3
"""Reference helper: Bakta on a genome FASTA (or bakta_proteins).

Resolve bakta_db via registry/references.yaml. Never download databases.

Example:
  export BAKTA_DB=/refdb/bakta_db_full/db-v6.0
  python annotate_bakta.py \\
    --genome /path/to/genome.fna \\
    --output-dir /path/to/job/analysis/shotgun-bakta \\
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


def _require_bakta_db(db: Path) -> Path:
    db = _require_dir(db, "Bakta DB")
    version = db / "version.json"
    if not version.is_file():
        raise FileNotFoundError(
            f"Bakta DB missing version.json: {db} (point at db-v6.0 / db, not the parent)"
        )
    return db


def run(
    fasta: Path,
    output_dir: Path,
    *,
    mode: str,
    threads: int,
    conda_env: str,
    bakta_db: Path,
    prefix: str | None,
    extra: list[str],
) -> Path:
    output_dir.mkdir(parents=True, exist_ok=True)
    fasta = _require_file(fasta, "input FASTA")
    bakta_db = _require_bakta_db(bakta_db)
    tool = "bakta_proteins" if mode == "proteins" else "bakta"
    base = prefix or fasta.stem
    cmd = [
        "conda",
        "run",
        "--no-capture-output",
        "-n",
        conda_env,
        tool,
        "--db",
        str(bakta_db),
        "--output",
        str(output_dir),
        "--prefix",
        base,
        "--force",
        "--threads",
        str(threads),
        *extra,
        str(fasta),
    ]
    print("Running:", " ".join(cmd), flush=True)
    subprocess.run(cmd, check=True)
    return output_dir


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--genome", type=Path, help="Nucleotide FASTA for bakta")
    p.add_argument("--protein", type=Path, help="Protein FASTA for bakta_proteins")
    p.add_argument("--mode", choices=("genome", "proteins"), default="genome")
    p.add_argument("--output-dir", type=Path, required=True)
    p.add_argument("--prefix", default=None)
    p.add_argument("--threads", type=int, default=8)
    p.add_argument("--conda-env", default=os.environ.get("CONDA_ENV_BAKTA", "bakta"))
    p.add_argument(
        "--db",
        type=Path,
        default=Path(os.environ["BAKTA_DB"]) if os.environ.get("BAKTA_DB") else None,
    )
    args, extra = p.parse_known_args()
    if args.db is None:
        raise SystemExit("Need --db or BAKTA_DB (registry/references.yaml bakta_db.path).")
    fasta = args.protein if args.mode == "proteins" else args.genome
    if fasta is None:
        raise SystemExit("Need --genome (or --protein with --mode proteins).")
    out = run(
        fasta,
        args.output_dir,
        mode=args.mode,
        threads=args.threads,
        conda_env=args.conda_env,
        bakta_db=args.db,
        prefix=args.prefix,
        extra=extra,
    )
    print(f"bakta: {out}")


if __name__ == "__main__":
    try:
        main()
    except subprocess.CalledProcessError as e:
        sys.exit(e.returncode)
