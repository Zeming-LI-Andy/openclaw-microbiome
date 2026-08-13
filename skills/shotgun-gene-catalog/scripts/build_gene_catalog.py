#!/usr/bin/env python3
"""Reference helpers for Prodigal ORF prediction and CD-HIT clustering.

Paths and conda envs are arguments — nothing is hardcoded to a specific machine.

Examples:
  python build_gene_catalog.py predict \\
    --contigs /job/stage/contigs.fasta \\
    --output-dir /job/analysis/shotgun-gene-catalog/predict

  python build_gene_catalog.py cluster \\
    --input /job/analysis/shotgun-gene-catalog/predict/proteins.faa \\
    --output-dir /job/analysis/shotgun-gene-catalog/cluster \\
    --identity 0.95 --coverage 0.9
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


def _conda_run(cmd: list[str], *, conda_env: str) -> None:
    full = ["conda", "run", "--no-capture-output", "-n", conda_env, *cmd]
    print("Running:", " ".join(full), flush=True)
    subprocess.run(full, check=True)


def predict(args: argparse.Namespace) -> dict[str, Path]:
    contigs = _require_file(Path(args.contigs), "contigs FASTA")
    out = Path(args.output_dir)
    out.mkdir(parents=True, exist_ok=True)

    proteins = out / "proteins.faa"
    genes = out / "genes.ffn"
    gff = out / "genes.gff"

    cmd = [
        "prodigal",
        "-i",
        str(contigs),
        "-a",
        str(proteins),
        "-d",
        str(genes),
        "-o",
        str(gff),
        "-f",
        "gff",
        "-p",
        args.procedure,
    ]
    _conda_run(cmd, conda_env=args.conda_env)

    results = {"proteins": proteins, "genes": genes, "gff": gff}
    for k, path in results.items():
        print(f"{k}: {path} ({'ok' if path.exists() else 'missing'})")
    return results


def cluster(args: argparse.Namespace) -> dict[str, Path]:
    inp = _require_file(Path(args.input), "input FASTA")
    out = Path(args.output_dir)
    out.mkdir(parents=True, exist_ok=True)

    if args.mode == "protein":
        tool = "cd-hit"
        nr = out / "nr_proteins.faa"
        word_size = args.word_size if args.word_size is not None else 5
    else:
        tool = "cd-hit-est"
        nr = out / "nr_genes.ffn"
        word_size = args.word_size if args.word_size is not None else 10

    cmd = [
        tool,
        "-i",
        str(inp),
        "-o",
        str(nr),
        "-c",
        str(args.identity),
        "-aS",
        str(args.coverage),
        "-n",
        str(word_size),
        "-T",
        str(args.threads),
        "-M",
        str(args.memory_mb),
    ]
    _conda_run(cmd, conda_env=args.conda_env)

    clstr = Path(str(nr) + ".clstr")
    results = {"nr": nr, "clstr": clstr}
    for k, path in results.items():
        print(f"{k}: {path} ({'ok' if path.exists() else 'missing'})")
    return results


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__)
    sub = p.add_subparsers(dest="cmd", required=True)

    pred = sub.add_parser("predict", help="prodigal ORF prediction")
    pred.add_argument("--contigs", required=True)
    pred.add_argument("--output-dir", required=True)
    pred.add_argument(
        "--conda-env",
        default=os.environ.get("CONDA_ENV_PRODIGAL", "eggnog_mapper"),
    )
    pred.add_argument(
        "--procedure",
        default="meta",
        choices=["meta", "single"],
        help="Prodigal -p (default: meta)",
    )

    clu = sub.add_parser("cluster", help="cd-hit / cd-hit-est clustering")
    clu.add_argument("--input", required=True, help="protein .faa or gene .ffn")
    clu.add_argument("--output-dir", required=True)
    clu.add_argument(
        "--conda-env",
        default=os.environ.get("CONDA_ENV_CDHIT", "mgx-base"),
    )
    clu.add_argument(
        "--mode",
        default="protein",
        choices=["protein", "nucleotide"],
        help="protein → cd-hit; nucleotide → cd-hit-est",
    )
    clu.add_argument("--identity", type=float, default=0.95, help="-c (default 0.95)")
    clu.add_argument("--coverage", type=float, default=0.9, help="-aS (default 0.9)")
    clu.add_argument(
        "--word-size",
        type=int,
        default=None,
        help="-n word size (default: 5 protein / 10 nucleotide)",
    )
    clu.add_argument("--threads", type=int, default=8, help="-T")
    clu.add_argument("--memory-mb", type=int, default=0, help="-M (0 = unlimited)")

    args = p.parse_args()
    if args.cmd == "predict":
        predict(args)
    else:
        cluster(args)


if __name__ == "__main__":
    try:
        main()
    except subprocess.CalledProcessError as e:
        sys.exit(e.returncode)
    except FileNotFoundError as e:
        print(e, file=sys.stderr)
        sys.exit(1)
