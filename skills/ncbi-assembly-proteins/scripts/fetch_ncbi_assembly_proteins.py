#!/usr/bin/env python3
"""Reference helper: download NCBI Assembly protein FASTA by organism name.

Reference only — adjust rate limits, filters (RefSeq vs GenBank), and output
layout for your job. Requires network.

Example:
  python fetch_ncbi_assembly_proteins.py \\
    --organism "Escherichia coli K-12" \\
    --output-dir /path/to/job/stage
"""

from __future__ import annotations

import argparse
import gzip
import json
import shutil
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path


EUTILS = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils"


def _get_json(url: str) -> dict:
    with urllib.request.urlopen(url) as resp:
        return json.loads(resp.read().decode())


def fetch(organism: str, output_dir: Path, *, sleep_s: float = 0.5) -> Path | None:
    output_dir.mkdir(parents=True, exist_ok=True)
    term = urllib.parse.quote(organism)
    search = _get_json(f"{EUTILS}/esearch.fcgi?db=assembly&term={term}&retmode=json")
    ids = search.get("esearchresult", {}).get("idlist", [])
    if not ids:
        print(f"No assembly hits for {organism!r}")
        return None

    for idx, assembly_id in enumerate(ids, 1):
        if idx > 1:
            time.sleep(sleep_s)
        summary = _get_json(
            f"{EUTILS}/esummary.fcgi?db=assembly&id={assembly_id}&retmode=json"
        )
        info = summary.get("result", {}).get(assembly_id, {})
        ftp = info.get("ftppath_refseq") or info.get("ftppath_genbank") or ""
        if not ftp:
            continue
        if ftp.startswith("ftp://"):
            ftp = "https://" + ftp[len("ftp://") :]
        name = Path(ftp).name
        protein = f"{name}_protein.faa.gz"
        url = f"{ftp}/{protein}"
        gz_path = output_dir / protein
        try:
            print(f"Downloading {url}")
            urllib.request.urlretrieve(url, gz_path)
        except urllib.error.HTTPError:
            continue
        if gz_path.stat().st_size <= 0:
            continue
        out = output_dir / protein.replace(".gz", "")
        with gzip.open(gz_path, "rb") as fin, open(out, "wb") as fout:
            shutil.copyfileobj(fin, fout)
        print(f"Wrote {out}")
        return out
    return None


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--organism", required=True)
    p.add_argument("--output-dir", type=Path, required=True)
    p.add_argument("--sleep", type=float, default=0.5, help="Delay between NCBI calls")
    args = p.parse_args()
    path = fetch(args.organism, args.output_dir, sleep_s=args.sleep)
    if path is None:
        raise SystemExit(1)
    print(path)


if __name__ == "__main__":
    main()
