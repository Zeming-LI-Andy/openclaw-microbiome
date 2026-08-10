#!/usr/bin/env python3
"""Reference helper: VFDB hit search via EggNOG-mapper Diamond (--no_annot).

Uses the same conda env as EggNOG-mapper. Resolve VFDB.dmnd via
registry/references.yaml (vfdb_dmnd: mount_path then local_path).

Example:
  export VFDB_DMND=/refdb/vfdb/VFDB.dmnd
  python annotate_vfdb.py \\
    --protein /path/to/proteins.faa \\
    --output-dir /path/to/job/analysis/shotgun-vfdb \\
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


def annotate(
    protein_faa: Path,
    output_dir: Path,
    *,
    threads: int,
    conda_env: str,
    vfdb_dmnd: Path,
) -> Path:
    output_dir.mkdir(parents=True, exist_ok=True)
    protein_faa = _require_file(protein_faa, "protein FASTA")
    base = protein_faa.stem
    cmd = [
        "conda",
        "run",
        "--no-capture-output",
        "-n",
        conda_env,
        "emapper.py",
        "-i",
        str(protein_faa),
        "--itype",
        "proteins",
        "--no_annot",
        "--dmnd_db",
        str(_require_file(vfdb_dmnd, "VFDB diamond DB")),
        "--cpu",
        str(threads),
        "-o",
        f"{base}_vfdb",
        "--output_dir",
        str(output_dir),
        "--override",
    ]
    print("Running:", " ".join(cmd), flush=True)
    subprocess.run(cmd, check=True)
    return output_dir / f"{base}_vfdb.emapper.seed_orthologs"


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--protein", type=Path, required=True)
    p.add_argument("--output-dir", type=Path, required=True)
    p.add_argument("--threads", type=int, default=8)
    p.add_argument(
        "--conda-env",
        default=os.environ.get("CONDA_ENV_EGGNOG", "eggnog_mapper"),
    )
    p.add_argument(
        "--vfdb-dmnd",
        type=Path,
        default=Path(os.environ["VFDB_DMND"]) if os.environ.get("VFDB_DMND") else None,
    )
    args = p.parse_args()
    if args.vfdb_dmnd is None:
        raise SystemExit("Need --vfdb-dmnd (or VFDB_DMND).")
    out = annotate(
        args.protein,
        args.output_dir,
        threads=args.threads,
        conda_env=args.conda_env,
        vfdb_dmnd=args.vfdb_dmnd,
    )
    print(f"vfdb: {out}")


if __name__ == "__main__":
    try:
        main()
    except subprocess.CalledProcessError as e:
        sys.exit(e.returncode)
