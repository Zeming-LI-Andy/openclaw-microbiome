#!/usr/bin/env python3
"""Reference helper: EggNOG-mapper on a protein FASTA.

Adapt paths, conda env, and flags to the host. Resolve DBs via
registry/references.yaml (mount_path then local_path).

Example:
  export EGGNOG_DATA_DIR=/refdb/eggnog
  export EGGNOG_DMND=/refdb/eggnog/bact_arch.dmnd
  python annotate_eggnog.py \\
    --protein /path/to/proteins.faa \\
    --output-dir /path/to/job/analysis/shotgun-eggnog \\
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


def annotate(
    protein_faa: Path,
    output_dir: Path,
    *,
    threads: int,
    conda_env: str,
    eggnog_data_dir: Path,
    eggnog_dmnd: Path,
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
        "-o",
        f"{base}_eggnog",
        "--output_dir",
        str(output_dir),
        "--dmnd_db",
        str(_require_file(eggnog_dmnd, "eggNOG diamond DB")),
        "--data_dir",
        str(_require_dir(eggnog_data_dir, "eggNOG data dir")),
        "--cpu",
        str(threads),
        "--override",
    ]
    print("Running:", " ".join(cmd), flush=True)
    subprocess.run(cmd, check=True)
    return output_dir / f"{base}_eggnog.emapper.annotations"


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
        "--eggnog-data-dir",
        type=Path,
        default=Path(os.environ["EGGNOG_DATA_DIR"]) if os.environ.get("EGGNOG_DATA_DIR") else None,
    )
    p.add_argument(
        "--eggnog-dmnd",
        type=Path,
        default=Path(os.environ["EGGNOG_DMND"]) if os.environ.get("EGGNOG_DMND") else None,
    )
    args = p.parse_args()
    if args.eggnog_data_dir is None or args.eggnog_dmnd is None:
        raise SystemExit(
            "Need --eggnog-data-dir and --eggnog-dmnd (or EGGNOG_DATA_DIR / EGGNOG_DMND)."
        )
    out = annotate(
        args.protein,
        args.output_dir,
        threads=args.threads,
        conda_env=args.conda_env,
        eggnog_data_dir=args.eggnog_data_dir,
        eggnog_dmnd=args.eggnog_dmnd,
    )
    print(f"eggnog: {out}")


if __name__ == "__main__":
    try:
        main()
    except subprocess.CalledProcessError as e:
        sys.exit(e.returncode)
