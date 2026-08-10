#!/usr/bin/env python3
"""Reference helpers for Aviary assemble / recover / annotate / cluster.

Paths and DB locations are **arguments or environment variables** — nothing is
hardcoded to a specific machine. Resolve DBs via registry/references.yaml,
then pass them here.

Examples:
  export GTDBTK_DATA_PATH=/refdb/aviary/gtdb
  export CHECKM2DB=/refdb/aviary/checkm2db
  export SINGLEM_METAPACKAGE_PATH=/refdb/aviary/singlem
  export EGGNOG_DATA_DIR=/refdb/aviary/eggnog

  python aviary_assemble_recover.py assemble \\
    --output-dir /job/analysis/shotgun-aviary/assemble \\
    -1 /job/stage/sample_R1.fq.gz -2 /job/stage/sample_R2.fq.gz

  python aviary_assemble_recover.py recover \\
    --output-dir /job/analysis/shotgun-aviary/recover \\
    --assembly /job/analysis/shotgun-aviary/assemble/assembly/final_contigs.fasta \\
    -1 /job/stage/sample_R1.fq.gz -2 /job/stage/sample_R2.fq.gz \\
    --gtdb-path \"$GTDBTK_DATA_PATH\" \\
    --checkm2-db-path \"$CHECKM2DB\" \\
    --singlem-metapackage-path \"$SINGLEM_METAPACKAGE_PATH\" \\
    --eggnog-db-path \"$EGGNOG_DATA_DIR\"

  python aviary_assemble_recover.py annotate \\
    --output-dir /job/analysis/shotgun-aviary/annotate \\
    --genome-fasta-directory /job/analysis/shotgun-aviary/recover/bins/final_bins \\
    --gtdb-path \"$GTDBTK_DATA_PATH\" \\
    --eggnog-db-path \"$EGGNOG_DATA_DIR\" \\
    --checkm2-db-path \"$CHECKM2DB\"

  python aviary_assemble_recover.py cluster \\
    --output-dir /job/analysis/shotgun-aviary/cluster \\
    --input-runs /job/analysis/shotgun-aviary/recover /other/job/recover
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


def _db_env(
    *,
    gtdb: str | None = None,
    checkm2: str | None = None,
    singlem: str | None = None,
    eggnog: str | None = None,
) -> dict[str, str]:
    env = os.environ.copy()
    for key, val in (
        ("GTDBTK_DATA_PATH", gtdb),
        ("CHECKM2DB", checkm2),
        ("SINGLEM_METAPACKAGE_PATH", singlem),
        ("EGGNOG_DATA_DIR", eggnog),
    ):
        if val:
            env[key] = val
        elif os.environ.get(key):
            env[key] = os.environ[key]
    if os.environ.get("CONDA_ENV_PATH"):
        env["CONDA_ENV_PATH"] = os.environ["CONDA_ENV_PATH"]
    return env


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
        cmd += [
            "--longreads",
            *lr,
            "--long_read_type",
            args.long_read_type,
            "--long-read-assembler",
            args.long_read_assembler,
        ]
    if args.use_megahit:
        cmd.append("--use-megahit")
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

    _conda_aviary(cmd, conda_env=args.conda_env, env=_db_env())
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

    env = _db_env(gtdb=gtdb, checkm2=checkm2, singlem=singlem, eggnog=eggnog)
    _conda_aviary(cmd, conda_env=args.conda_env, env=env)
    results = {
        "bin_info": out / "bins" / "bin_info.tsv",
        "final_bins": out / "bins" / "final_bins",
        "taxonomy": out / "taxonomy",
    }
    for k, path in results.items():
        print(f"{k}: {path} ({'ok' if path.exists() else 'missing'})")
    return results


def annotate(args: argparse.Namespace) -> dict[str, Path]:
    bins = Path(args.genome_fasta_directory)
    if not bins.is_dir():
        raise SystemExit(f"genome FASTA directory not found: {bins}")

    gtdb = args.gtdb_path or os.environ.get("GTDBTK_DATA_PATH")
    eggnog = args.eggnog_db_path or os.environ.get("EGGNOG_DATA_DIR")
    checkm2 = args.checkm2_db_path or os.environ.get("CHECKM2DB")
    missing = [
        name
        for name, val in (("gtdb", gtdb), ("eggnog", eggnog), ("checkm2", checkm2))
        if not val
    ]
    if missing:
        raise SystemExit(
            "annotate needs DB paths (flags or env): " + ", ".join(missing)
        )

    out = Path(args.output_dir)
    out.mkdir(parents=True, exist_ok=True)

    cmd = [
        "aviary",
        "annotate",
        "-d",
        str(bins),
        "-x",
        args.fasta_extension,
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
        "--eggnog-db-path",
        eggnog,
        "--checkm2-db-path",
        checkm2,
    ]
    env = _db_env(gtdb=gtdb, checkm2=checkm2, eggnog=eggnog)
    _conda_aviary(cmd, conda_env=args.conda_env, env=env)
    results = {
        "eggnog": out / "annotation" / "eggnog",
        "gtdbtk": out / "annotation" / "gtdbtk",
    }
    for k, path in results.items():
        print(f"{k}: {path} ({'ok' if path.exists() else 'missing'})")
    return results


def cluster(args: argparse.Namespace) -> dict[str, Path]:
    runs = _list(args.input_runs)
    if not runs:
        raise SystemExit("Need --input-runs with one or more Aviary recover output dirs")

    out = Path(args.output_dir)
    out.mkdir(parents=True, exist_ok=True)

    cmd = [
        "aviary",
        "cluster",
        "-i",
        *runs,
        "-t",
        str(args.threads),
        "-n",
        str(args.n_cores),
        "-o",
        str(out),
        "--ani",
        str(args.ani),
    ]
    if args.min_completeness is not None:
        cmd += ["--min-completeness", str(args.min_completeness)]
    if args.max_contamination is not None:
        cmd += ["--max-contamination", str(args.max_contamination)]

    _conda_aviary(cmd, conda_env=args.conda_env, env=os.environ.copy())
    results = {"dereplicated_bins": out / "dereplicated_bins"}
    for k, path in results.items():
        print(f"{k}: {path} ({'ok' if path.exists() else 'missing'})")
    return results


def _add_common(sp: argparse.ArgumentParser, *, reads: bool = True) -> None:
    sp.add_argument("--output-dir", required=True)
    sp.add_argument("--conda-env", default=os.environ.get("CONDA_ENV_AVIARY", "aviary"))
    sp.add_argument("--threads", type=int, default=12)
    sp.add_argument("--n-cores", type=int, default=12)
    sp.add_argument("--pplacer-threads", type=int, default=8)
    if reads:
        sp.add_argument("-1", "--short-reads-1", nargs="+", dest="short_reads_1")
        sp.add_argument("-2", "--short-reads-2", nargs="+", dest="short_reads_2")
        sp.add_argument("--long-reads", nargs="+")
        sp.add_argument("--long-read-type", default="ont")
        sp.add_argument("--coassemble", action=argparse.BooleanOptionalAction, default=None)


def _add_db_flags(sp: argparse.ArgumentParser) -> None:
    sp.add_argument("--gtdb-path")
    sp.add_argument("--checkm2-db-path")
    sp.add_argument("--singlem-metapackage-path")
    sp.add_argument("--eggnog-db-path")


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__)
    sub = p.add_subparsers(dest="cmd", required=True)

    a = sub.add_parser("assemble", help="aviary assemble")
    _add_common(a)
    a.add_argument(
        "--use-megahit",
        action="store_true",
        help="Use MEGAHIT instead of metaSPAdes for short-read assembly",
    )
    a.add_argument(
        "--long-read-assembler",
        default="myloasm",
        choices=["myloasm", "flye"],
        help="Long-read assembler when --long-reads is set (default: myloasm)",
    )

    r = sub.add_parser("recover", help="aviary recover")
    _add_common(r)
    r.add_argument("--assembly")
    _add_db_flags(r)
    r.add_argument(
        "--binning-only",
        action=argparse.BooleanOptionalAction,
        default=False,
        help="Skip post-binning taxonomy/annotation in recover (default: full recover)",
    )
    r.add_argument("--extra-binners", nargs="+")
    r.add_argument("--skip-binners", nargs="+")

    an = sub.add_parser("annotate", help="aviary annotate (MAGs)")
    _add_common(an, reads=False)
    an.add_argument(
        "--genome-fasta-directory",
        "-d",
        required=True,
        help="Directory of MAG FASTA files (e.g. recover/bins/final_bins)",
    )
    an.add_argument(
        "--fasta-extension",
        "-x",
        default="fna",
        help="MAG file extension without dot (default: fna)",
    )
    _add_db_flags(an)

    cl = sub.add_parser("cluster", help="aviary cluster (dereplicate runs)")
    _add_common(cl, reads=False)
    cl.add_argument(
        "--input-runs",
        "-i",
        nargs="+",
        required=True,
        help="Previous Aviary recover (or complete) output directories",
    )
    cl.add_argument("--ani", type=float, default=97.0, help="ANI threshold (default 97)")
    cl.add_argument("--min-completeness", type=float, default=None)
    cl.add_argument("--max-contamination", type=float, default=None)

    args = p.parse_args()
    if args.cmd == "assemble":
        assemble(args)
    elif args.cmd == "recover":
        recover(args)
    elif args.cmd == "annotate":
        annotate(args)
    else:
        cluster(args)


if __name__ == "__main__":
    try:
        main()
    except subprocess.CalledProcessError as e:
        sys.exit(e.returncode)
    except SystemExit:
        raise
    except Exception as e:
        print(e, file=sys.stderr)
        sys.exit(1)
