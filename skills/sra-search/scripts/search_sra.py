#!/usr/bin/env python3
"""Reference: search NCBI SRA metadata (esearch + esummary). Does NOT download FASTQ.

Requires network. Optional env: NCBI_API_KEY, NCBI_EMAIL.

Example:
  python search_sra.py --query "gut microbiome IBD 16S" --organism "Homo sapiens" --retmax 10
  python search_sra.py --query SRR390728 --json-out /job/analysis/sra-search/hits.json
"""

from __future__ import annotations

import argparse
import json
import os
import re
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Any

EUTILS = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils"
DEFAULT_RETMAX = 10
MAX_RETMAX = 50


def _auth() -> dict[str, str]:
    params: dict[str, str] = {"tool": "openclaw-microbiome-sra-search"}
    if os.environ.get("NCBI_API_KEY"):
        params["api_key"] = os.environ["NCBI_API_KEY"].strip()
    if os.environ.get("NCBI_EMAIL"):
        params["email"] = os.environ["NCBI_EMAIL"].strip()
    return params


def _get_json(endpoint: str, params: dict[str, Any]) -> dict:
    q = urllib.parse.urlencode({**params, **_auth()})
    url = f"{EUTILS}/{endpoint}?{q}"
    req = urllib.request.Request(url, headers={"User-Agent": "openclaw-microbiome-sra-search/0.1"})
    with urllib.request.urlopen(req, timeout=60) as resp:
        return json.loads(resp.read().decode())


def _parse_xml_fragment(fragment: str) -> ET.Element | None:
    text = (fragment or "").strip()
    if not text:
        return None
    try:
        return ET.fromstring(f"<Root>{text}</Root>")
    except ET.ParseError:
        cleaned = re.sub(r"&(?!amp;|lt;|gt;|quot;|apos;)", "&amp;", text)
        try:
            return ET.fromstring(f"<Root>{cleaned}</Root>")
        except ET.ParseError:
            return None


def _text(root: ET.Element | None, tag: str, attr: str | None = None) -> str:
    if root is None:
        return ""
    el = root.find(f".//{tag}")
    if el is None:
        return ""
    if attr:
        return (el.attrib.get(attr) or "").strip()
    return (el.text or "").strip()


def _records_from_summary(uid: str, item: dict[str, Any]) -> list[dict[str, Any]]:
    exp_root = _parse_xml_fragment(str(item.get("expxml") or ""))
    runs_root = _parse_xml_fragment(str(item.get("runs") or ""))
    organism_el = exp_root.find(".//Organism") if exp_root is not None else None
    organism = ""
    if organism_el is not None:
        organism = (
            organism_el.attrib.get("ScientificName")
            or _text(exp_root, "ScientificName")
            or (organism_el.text or "")
        ).strip()
    platform_el = exp_root.find(".//Platform") if exp_root is not None else None
    platform = (platform_el.text or "").strip() if platform_el is not None else ""
    instrument = platform_el.attrib.get("instrument_model", "").strip() if platform_el is not None else ""
    base = {
        "uid": uid,
        "title": (_text(exp_root, "Title") or str(item.get("title") or ""))[:300],
        "organism": organism,
        "platform": platform,
        "instrument": instrument,
        "library_strategy": _text(exp_root, "LIBRARY_STRATEGY") or _text(exp_root, "Strategy"),
        "bioproject": _text(exp_root, "Bioproject"),
        "biosample": _text(exp_root, "Biosample"),
        "experiment": _text(exp_root, "Experiment", "acc"),
    }
    runs = []
    if runs_root is not None:
        for run in runs_root.findall(".//Run"):
            acc = (run.attrib.get("acc") or "").strip()
            if acc:
                runs.append(
                    {
                        "accession": acc,
                        "spots": (run.attrib.get("total_spots") or "").strip(),
                        "bases": (run.attrib.get("total_bases") or "").strip(),
                    }
                )
    if not runs:
        acc = base["experiment"] or uid
        return [
            {
                **base,
                "accession": acc,
                "spots": _text(exp_root, "Statistics", "total_spots"),
                "bases": _text(exp_root, "Statistics", "total_bases"),
                "sra_url": f"https://www.ncbi.nlm.nih.gov/sra/{acc}",
            }
        ]
    out = []
    for run in runs:
        acc = run["accession"]
        out.append(
            {
                **base,
                "accession": acc,
                "spots": run.get("spots") or "",
                "bases": run.get("bases") or "",
                "sra_url": f"https://www.ncbi.nlm.nih.gov/sra/{acc}",
            }
        )
    return out


def search(
    query: str,
    *,
    organism: str | None = None,
    library_strategy: str | None = None,
    retmax: int = DEFAULT_RETMAX,
) -> tuple[list[dict[str, Any]], int, str]:
    parts = [query.strip()]
    if organism:
        parts.append(f"{organism.strip()}[Organism]")
    if library_strategy:
        parts.append(f"{library_strategy.strip()}[Strategy]")
    term = " AND ".join(parts)
    retmax = max(1, min(int(retmax), MAX_RETMAX))

    es = _get_json(
        "esearch.fcgi",
        {"db": "sra", "term": term, "retmode": "json", "retmax": str(retmax)},
    )
    result = es.get("esearchresult") or {}
    ids = [str(i) for i in (result.get("idlist") or [])]
    total = int(result.get("count") or len(ids) or 0)
    if not ids:
        return [], total, term

    sm = _get_json(
        "esummary.fcgi",
        {"db": "sra", "id": ",".join(ids), "retmode": "json"},
    )
    block = sm.get("result") or {}
    records: list[dict[str, Any]] = []
    for uid in ids:
        item = block.get(uid)
        if isinstance(item, dict):
            records.extend(_records_from_summary(uid, item))

    q_acc = query.strip().upper()
    if re.fullmatch(r"(SRR|ERR|DRR)\d+", q_acc):
        matched = [r for r in records if str(r.get("accession", "")).upper() == q_acc]
        if matched:
            records = matched
    return records[:retmax], total, term


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--query", required=True)
    p.add_argument("--organism")
    p.add_argument("--library-strategy")
    p.add_argument("--retmax", type=int, default=DEFAULT_RETMAX)
    p.add_argument("--json-out", type=Path, help="Optional path to write JSON results")
    args = p.parse_args()

    records, total, term = search(
        args.query,
        organism=args.organism,
        library_strategy=args.library_strategy,
        retmax=args.retmax,
    )
    print(f"SRA search query: {term}")
    print(f"NCBI reported {total} hit(s); showing {len(records)}.")
    print()
    if not records:
        print("No SRA records found.")
    for i, rec in enumerate(records, 1):
        print(f"{i}. {rec.get('accession')}")
        print(f"   Title: {rec.get('title')}")
        print(f"   Organism: {rec.get('organism')}")
        print(f"   Platform/Instrument: {rec.get('platform')} / {rec.get('instrument')}")
        print(f"   Strategy: {rec.get('library_strategy')}")
        print(f"   BioProject/BioSample: {rec.get('bioproject')} / {rec.get('biosample')}")
        print(f"   Spots/Bases: {rec.get('spots')} / {rec.get('bases')}")
        print(f"   URL: {rec.get('sra_url')}")
        print()
    print("Metadata only — no FASTQ/SRA files were downloaded.")

    if args.json_out:
        args.json_out.parent.mkdir(parents=True, exist_ok=True)
        payload = {
            "query": term,
            "total_count": total,
            "returned": len(records),
            "records": records,
        }
        args.json_out.write_text(json.dumps(payload, ensure_ascii=False, indent=2))
        print(f"Wrote {args.json_out}")


if __name__ == "__main__":
    main()
