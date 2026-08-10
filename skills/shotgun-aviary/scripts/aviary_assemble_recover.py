#!/usr/bin/env python3
"""Reference helpers for Aviary assemble / recover.

Paths and DB locations are **arguments or environment variables** — nothing is
hardcoded to a specific machine. Resolve DBs via registry/references.yaml
(mount_path then local_path), then pass them here.

Examples:
  export GTDBTK_DATA_PATH=/refdb/aviary/gtdb
  export CHECKM2DB=/refdb/aviary/checkm2db
  export SINGLEM_METAPACKAGE_PATH=/refdb/aviary/singlem
  export EGGNOG_DATA_DIR=/refdb/aviary/eggnog

  python aviary_assemble_recover.py assemble \\
    --output-dir /job/analysis/shotgun-aviary/assemble \\
    -1 /job/stage/sample_R1.fq.gz -2 /job/stage/sample_R2.fq.gz \\
    --threads 12 --n-cores 12

  python aviary_assemble_recover.py recover \\
    --output-dir /job/analysis/shotgun-aviary/recover \\
    --assembly /job/analysis/shotgun-aviary/assemble/assembly/final_contigs.fasta \\
    -1 /job/stage/sample_R1.fq.gz -2 /job/stage/sample_R2.fq.gz \\
    --gtdb-path \"$GTDBTK_DATA_PATH\" \\
    --checkm2-db-path \"$CHECKM2DB\" \\
    --singlem-metapackage-path \"$SINGLEM_METAPACKAGE_PATH\" \\
    --eggnog-db-path \"$EGGNOG_DATA_DIR\"
"""

from __future__ import annotations

import argparse
import os
import subprocess
import sys
from pathlib import Path


def _list(val: list[str] | None) -> list[str]:
    return list(val or [])


def _conda_aviary(cmd: list[str], *, conda_env: str, env: dict[str, str]) -> None:
    full = ["conda", "run", "--no-capture-output", "-n", conda_env, *cmd]
    print("Running:", " ".join(full), flush=True)
    subprocess.run(full, check=True, env=env)


def assemble(args: argparse.Namespace) -> Path:
    if not args.short_reads_1 and not args.long_reads:
        raise SystemExit("Need --short-reads-1 and/or --long-reads")
    if args.short_reads_2 and not args.short_reads_1:
        raise SystemExit("--short-reads-2 requires --short-reads-1")

    sr1 = _list(args.short_reads_1)
    sr2 = _list(args.short_reads_2)
    lr = _list(args.long_reads)
    if sr1 and not sr2 and not lr:
        sr2 = list(sr1)

    out = Path(args.output_dir)
    out.mkdir(parents=True, exist_ok=True)

    cmd = ["aviary", "assemble"]
    if sr1:
        cmd += ["-1", *sr1]
    if sr2:
        cmd += ["-2", *sr2]
    if lr:
        cmd += ["--longreads", *lr, "--long_read_type", args.long_read_type]
    cmd += [
        "-t",
        str(args.threads),
        "-n",
        str(args.n_cores),
        "-p",
        str(args.pplacer_threads),
        "--output",
        str(out),
    ]
    if args.coassemble is not None and (len(sr1) > 1 or len(lr) > 1):
        cmd += ["--coassemble", "yes" if args.coassemble else "no"]

    env = os.environ.copy()
    for key in (
        "GTDBTK_DATA_PATH",
        "EGGNOG_DATA_DIR",
        "SINGLEM_METAPACKAGE_PATH",
        "CHECKM2DB",
        "CONDA_ENV_PATH",
    ):
        if os.environ.get(key):
            env[key] = os.environ[key]

    _conda_aviary(cmd, conda_env=args.conda_env, env=env)
    contigs = out / "assembly" / "final_contigs.fasta"
    print("Expected contigs:", contigs)
    return contigs


def recover(args: argparse.Namespace) -> dict[str, Path]:
    if not args.assembly and not args.short_reads_1 and not args.long_reads:
        raise SystemExit("Need --assembly and/or reads")

    out = Path(args.output_dir)
    out.mkdir(parents=True, exist_ok=True)
    sr1 = _list(args.short_reads_1)
    sr2 = _list(args.short_reads_2)
    lr = _list(args.long_reads)
    if not args.assembly and sr1 and not sr2 and not lr:
        sr2 = list(sr1)

    gtdb = args.gtdb_path or os.environ.get("GTDBTK_DATA_PATH")
    checkm2 = args.checkm2_db_path or os.environ.get("CHECKM2DB")
    singlem = args.singlem_metapackage_path or os.environ.get("SINGLEM_METAPACKAGE_PATH")
    eggnog = args.eggnog_db_path or os.environ.get("EGGNOG_DATA_DIR")
    missing = [
        name
        for name, val in (
            ("gtdb", gtdb),
            ("checkm2", checkm2),
            ("singlem", singlem),
            ("eggnog", eggnog),
        )
        if not val
    ]
    if missing:
        raise SystemExit(
            "recover needs DB paths (flags or env): " + ", ".join(missing)
        )

    cmd = ["aviary", "recover"]
    if args.assembly:
        cmd += ["-a", args.assembly]
    if sr1:
        cmd += ["-1", *sr1]
    if sr2:
        cmd += ["-2", *sr2]
    if lr:
        cmd += ["-l", *lr, "-z", args.long_read_type]
    cmd += [
        "-t",
        str(args.threads),
        "-n",
        str(args.n_cores),
        "-p",
        str(args.pplacer_threads),
        "-o",
        str(out),
        "--gtdb-path",
        gtdb,
        "--checkm2-db-path",
        checkm2,
        "--singlem-metapackage-path",
        singlem,
        "--eggnog-db-path",
        eggnog,
    ]
    if args.binning_only:
        cmd.append("--binning-only")
    if args.extra_binners:
        cmd += ["--extra-binners", *args.extra_binners]
    if args.skip_binners:
        cmd += ["--skip-binners", *args.skip_binners]

    env = os.environ.copy()
    env["GTDBTK_DATA_PATH"] = gtdb
    env["CHECKM2DB"] = checkm2
    env["SINGLEM_METAPACKAGE_PATH"] = singlem
    env["EGGNOG_DATA_DIR"] = eggnog

    _conda_aviary(cmd, conda_env=args.conda_env, env=env)
    results = {
        "bin_info": out / "bins" / "bin_info.tsv",
        "final_bins": out / "bins" / "final_bins",
        "taxonomy": out / "taxonomy",
    }
    for k, path in results.items():
        print(f"{k}: {path} ({'ok' if path.exists() else 'missing'})")
    return results


def _add_common(sp: argparse.ArgumentParser) -> None:
    sp.add_argument("--output-dir", required=True)
    sp.add_argument("--conda-env", default=os.environ.get("CONDA_ENV_AVIARY", "aviary"))
    sp.add_argument("-1", "--short-reads-1", nargs="+", dest="short_reads_1")
    sp.add_argument("-2", "--short-reads-2", nargs="+", dest="short_reads_2")
    sp.add_argument("--long-reads", nargs="+")
    sp.add_argument("--long-read-type", default="ont")
    sp.add_argument("--threads", type=int, default=12)
    sp.add_argument("--n-cores", type=int, default=12)
    sp.add_argument("--pplacer-threads", type=int, default=8)
    sp.add_argument("--coassemble", action=argparse.BooleanOptionalAction, default=None)


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__)
    sub = p.add_subparsers(dest="cmd", required=True)

    a = sub.add_parser("assemble", help="aviary assemble")
    _add_common(a)

    r = sub.add_parser("recover", help="aviary recover")
    _add_common(r)
    r.add_argument("--assembly")
    r.add_argument("--gtdb-path")
    r.add_argument("--checkm2-db-path")
    r.add_argument("--singlem-metapackage-path")
    r.add_argument("--eggnog-db-path")
    r.add_argument("--binning-only", action=argparse.BooleanOptionalAction, default=True)
    r.add_argument("--extra-binners", nargs="+")
    r.add_argument("--skip-binners", nargs="+")

    args = p.parse_args()
    if args.cmd == "assemble":
        assemble(args)
    else:
        recover(args)


if __name__ == "__main__":
    try:
        main()
    except subprocess.CalledProcessError as e:
        sys.exit(e.returncode)
