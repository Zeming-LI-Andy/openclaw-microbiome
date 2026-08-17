#!/usr/bin/env python3
"""Reference helper: gapseq find / find-transport / doall.

Resolve gapseq_sequences via registry/references.yaml. Always pass -O on
find/doall. Never run gapseq update-sequences.

Example:
  export GAPSEQ_SEQ_DIR=/refdb/gapseq_db/dat/seq
  python run_gapseq.py find \\
    --genome /path/to/genome.faa \\
    --output-dir /path/to/job/analysis/shotgun-gapseq/find \\
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


def _conda(env: str, *args: str) -> list[str]:
    return ["conda", "run", "--no-capture-output", "-n", env, "gapseq", *args]


def run(
    subcmd: str,
    genome: Path,
    output_dir: Path,
    *,
    conda_env: str,
    seq_dir: Path | None,
    threads: int,
    pathways: str,
    taxonomy: str,
    aligner: str,
    extra: list[str],
) -> Path:
    output_dir.mkdir(parents=True, exist_ok=True)
    genome = _require_file(genome, "genome FASTA")
    cmd: list[str]
    if subcmd == "find-transport":
        cmd = _conda(
            conda_env,
            "find-transport",
            "-f",
            str(output_dir),
            "-K",
            str(threads),
            "-A",
            aligner,
            *extra,
            str(genome),
        )
    elif subcmd in {"find", "doall"}:
        if seq_dir is None:
            raise SystemExit("Need --seq-dir or GAPSEQ_SEQ_DIR for find/doall.")
        seq_dir = _require_dir(seq_dir, "gapseq sequence DB (-D)")
        cmd = _conda(
            conda_env,
            subcmd,
            "-f",
            str(output_dir),
            "-D",
            str(seq_dir),
            "-O",
            "-t",
            taxonomy,
            "-K",
            str(threads),
            "-A",
            aligner,
            *extra,
            str(genome),
        )
        if subcmd == "find":
            # insert -p before genome
            cmd = cmd[:-1] + ["-p", pathways, cmd[-1]]
    else:
        raise SystemExit(f"unsupported subcommand: {subcmd}")
    print("Running:", " ".join(cmd), flush=True)
    subprocess.run(cmd, check=True)
    return output_dir


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("subcommand", choices=("find", "find-transport", "doall"))
    p.add_argument("--genome", type=Path, required=True)
    p.add_argument("--output-dir", type=Path, required=True)
    p.add_argument("--threads", type=int, default=8)
    p.add_argument("--pathways", default="all", help="find -p (default: all)")
    p.add_argument("--taxonomy", default="auto", help="Bacteria|Archaea|auto")
    p.add_argument("--aligner", default="diamond", help="blast|diamond|mmseqs2")
    p.add_argument("--conda-env", default=os.environ.get("CONDA_ENV_GAPSEQ", "gapseq"))
    p.add_argument(
        "--seq-dir",
        type=Path,
        default=Path(os.environ["GAPSEQ_SEQ_DIR"]) if os.environ.get("GAPSEQ_SEQ_DIR") else None,
    )
    args, extra = p.parse_known_args()
    out = run(
        args.subcommand,
        args.genome,
        args.output_dir,
        conda_env=args.conda_env,
        seq_dir=args.seq_dir,
        threads=args.threads,
        pathways=args.pathways,
        taxonomy=args.taxonomy,
        aligner=args.aligner,
        extra=extra,
    )
    print(f"gapseq {args.subcommand}: {out}")


if __name__ == "__main__":
    try:
        main()
    except subprocess.CalledProcessError as e:
        sys.exit(e.returncode)
