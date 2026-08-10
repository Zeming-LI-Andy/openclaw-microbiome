#!/usr/bin/env python3
"""Reference helper: CARD RGI on a protein FASTA.

Resolve card.json via registry/references.yaml (card_db: mount_path then
local_path). Adapt env name and RGI flags to the host.

Example:
  export CARD_JSON=/refdb/card/card.json
  python annotate_rgi.py \\
    --protein /path/to/proteins.faa \\
    --output-dir /path/to/job/analysis/shotgun-rgi \\
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
    card_json: Path | None,
) -> Path:
    output_dir.mkdir(parents=True, exist_ok=True)
    protein_faa = _require_file(protein_faa, "protein FASTA")
    base = protein_faa.stem
    out_prefix = output_dir / f"{base}_card"
    env = os.environ.copy()
    if card_json is not None:
        env["CARD_JSON"] = str(_require_file(card_json, "CARD JSON"))
    cmd = [
        "conda",
        "run",
        "--no-capture-output",
        "-n",
        conda_env,
        "rgi",
        "main",
        "--input_sequence",
        str(protein_faa),
        "--output_file",
        str(out_prefix),
        "--clean",
        "-t",
        "protein",
        "--num_threads",
        str(threads),
    ]
    print("Running:", " ".join(cmd), flush=True)
    subprocess.run(cmd, check=True, env=env)
    return Path(f"{out_prefix}.txt")


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--protein", type=Path, required=True)
    p.add_argument("--output-dir", type=Path, required=True)
    p.add_argument("--threads", type=int, default=8)
    p.add_argument("--conda-env", default=os.environ.get("CONDA_ENV_RGI", "rgi"))
    p.add_argument(
        "--card-json",
        type=Path,
        default=Path(os.environ["CARD_JSON"]) if os.environ.get("CARD_JSON") else None,
    )
    args = p.parse_args()
    out = annotate(
        args.protein,
        args.output_dir,
        threads=args.threads,
        conda_env=args.conda_env,
        card_json=args.card_json,
    )
    print(f"card: {out}")


if __name__ == "__main__":
    try:
        main()
    except subprocess.CalledProcessError as e:
        sys.exit(e.returncode)
